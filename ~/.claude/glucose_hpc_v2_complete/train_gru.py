"""GRU (glucose history) + MLP (other features), multi-task: t30 + t60 regression + hypo classification.
v2 options:  --seeds N        train N runs with different seeds and AVERAGE them (more stable)
             --low_weight W   errors on true glucose < --low_below (default 90) count W times more
Only for the time-series datasets.   python train_gru.py --raw_dir data --datasets cgm_t1dm_t2dm ohhim
Needs PyTorch (GPU recommended). Saves val/test predictions to results/preds/ (used by evaluate_models.py)."""
import argparse
import numpy as np, pandas as pd, torch, torch.nn as nn
from pathlib import Path
from common import (SEQ, add_args, choose_threshold, evaluate, is_glucose, load, prepare, save_metrics, save_preds,
                    splits, task_of)

ap = add_args(argparse.ArgumentParser(), datasets=list(SEQ))
ap.add_argument("--epochs", type=int, default=60)
ap.add_argument("--batch", type=int, default=512)
ap.add_argument("--lr", type=float, default=1e-3)
ap.add_argument("--hidden", type=int, default=64)
ap.add_argument("--patience", type=int, default=8)
ap.add_argument("--seeds", type=int, default=1)
a = ap.parse_args()
assert all(d in SEQ for d in a.datasets), f"GRU supports only {list(SEQ)}"
dev = "cuda" if torch.cuda.is_available() else "cpu"
prepare(a); res = Path(a.results_dir); res.mkdir(exist_ok=True)


class Net(nn.Module):
    def __init__(s, n_stat, n_reg, n_clf, h):
        super().__init__()
        s.gru = nn.GRU(1, h, num_layers=2, batch_first=True, dropout=0.1)
        s.mlp = nn.Sequential(nn.Linear(n_stat, h), nn.ReLU(), nn.Dropout(0.1))
        s.head = nn.Sequential(nn.Linear(2 * h, h), nn.ReLU(), nn.Linear(h, n_reg + n_clf))
        s.n_reg = n_reg

    def forward(s, xs, xt):
        _, hn = s.gru(xs)
        o = s.head(torch.cat([hn[-1], s.mlp(xt)], 1))
        return o[:, :s.n_reg], o[:, s.n_reg:]


all_rows = []
for name in a.datasets:
    df, feats, targets, sc = load(a, name)
    S = splits(df); seq_cols = SEQ[name]; static = [f for f in feats if f not in seq_cols]
    reg_t = [t for t in targets if task_of(df, t) == "reg"]; clf_t = [t for t in targets if task_of(df, t) == "clf"]
    mu, sd = S["train"][reg_t].mean().to_numpy(), S["train"][reg_t].std().to_numpy()
    f32 = lambda x: torch.tensor(np.asarray(x), dtype=torch.float32)
    T = {k: (f32(d[seq_cols].to_numpy())[..., None], f32(d[static].to_numpy()),
             f32(((d[reg_t].to_numpy() - mu) / sd)), f32(d[clf_t].to_numpy())) for k, d in S.items()}
    W = f32(np.where(S["train"][reg_t].to_numpy() < a.low_below, a.low_weight, 1.0))   # weight on low glucose

    def predict(net, split):
        net.eval(); R, C = [], []
        with torch.no_grad():
            for i in range(0, len(T[split][0]), 4096):
                r, c = net(T[split][0][i:i + 4096].to(dev), T[split][1][i:i + 4096].to(dev))
                R.append(r.cpu()); C.append(torch.sigmoid(c).cpu())
        return torch.cat(R).numpy() * sd + mu, torch.cat(C).numpy()

    def fit_one(seed):
        torch.manual_seed(seed); np.random.seed(seed)
        net = Net(len(static), len(reg_t), len(clf_t), a.hidden).to(dev)
        opt = torch.optim.AdamW(net.parameters(), lr=a.lr, weight_decay=1e-4)
        sched = torch.optim.lr_scheduler.ReduceLROnPlateau(opt, factor=0.5, patience=3)
        pos = T["train"][3].mean(0).clamp(min=1e-3)
        bce = nn.BCEWithLogitsLoss(pos_weight=((1 - pos) / pos).to(dev))
        best, bad, state = 1e18, 0, None
        for ep in range(a.epochs):
            net.train(); n = len(T["train"][0]); perm = torch.randperm(n); tot = 0
            for i in range(0, n, a.batch):
                ix = perm[i:i + a.batch]; xs, xt, yr, yc = (z[ix].to(dev) for z in T["train"]); w = W[ix].to(dev)
                r, c = net(xs, xt)
                loss = (nn.functional.smooth_l1_loss(r, yr, reduction="none") * w).sum() / w.sum() + 0.3 * bce(c, yc)
                opt.zero_grad(); loss.backward(); nn.utils.clip_grad_norm_(net.parameters(), 1.0); opt.step()
                tot += loss.item() * len(ix)
            vr, _ = predict(net, "val")
            vloss = float(np.sqrt(((vr - S["val"][reg_t].to_numpy()) ** 2).mean()))
            sched.step(vloss); print(f"[{name} seed {seed}] epoch {ep + 1} train_loss {tot / n:.4f} val_RMSE {vloss:.2f}", flush=True)
            if vloss < best - 1e-3: best, bad, state = vloss, 0, {k: v.clone() for k, v in net.state_dict().items()}
            else:
                bad += 1
                if bad >= a.patience: break
        net.load_state_dict(state)
        torch.save(state, res / (f"gru__{name}.pt" if seed == a.seed else f"gru__{name}_seed{seed}.pt"))
        return {s: predict(net, s) for s in ("val", "test")}

    runs = [fit_one(a.seed + k) for k in range(a.seeds)]
    avg = {s: (np.mean([r[s][0] for r in runs], 0), np.mean([r[s][1] for r in runs], 0)) for s in ("val", "test")}
    P = {}
    for s in ("val", "test"):
        r, c = avg[s]
        for j, t in enumerate(reg_t):
            all_rows.append(dict(dataset=name, model="gru", target=t, split=s, **evaluate("reg", S[s][t], r[:, j], glucose=is_glucose(t))))
            P[f"{t}__{s}"] = r[:, j]
        for j, t in enumerate(clf_t):
            thr = choose_threshold(S["val"][t], avg["val"][1][:, j], a.min_recall)
            all_rows.append(dict(dataset=name, model="gru", target=t, split=s, **evaluate("clf", S[s][t], c[:, j], thr)))
            P[f"{t}__{s}"] = c[:, j]
    save_preds(res, "gru", name, P)
save_metrics(pd.DataFrame(all_rows), res, "gru")
