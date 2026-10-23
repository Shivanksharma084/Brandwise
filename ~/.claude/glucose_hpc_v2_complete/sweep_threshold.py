"""Threshold sweep for an ALREADY TRAINED model (no retraining, runs in seconds).
Shows precision / recall / F1 / false alarms at many thresholds, and what happens on TEST when the threshold
is chosen on VAL for a recall target.

  python sweep_threshold.py --raw_dir data --dataset ohhim                       # GRU  (needs results/gru__ohhim.pt)
  python sweep_threshold.py --raw_dir data --dataset ohhim --model lgbm          # also: xgb | rf | linear
Options: --target target_hypo_60  --hidden 64 (must equal the --hidden used in training)  --results_dir results
Run it from the glucose_hpc folder. Needs common.py from the same folder (use the updated one)."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from common import SEQ, add_args, choose_threshold, load, prepare, splits, task_of

ap = add_args(argparse.ArgumentParser())
ap.add_argument("--dataset", required=True, choices=["smart_wearable", "glucotwin", "cgm_t1dm_t2dm", "ohhim"])
ap.add_argument("--model", default="gru", choices=["gru", "lgbm", "xgb", "rf", "linear", "ensemble", "ensemble_cal"])
ap.add_argument("--target", default="target_hypo_60")
ap.add_argument("--hidden", type=int, default=64)


def probs_gru(a, df, feats, targets):
    import torch, torch.nn as nn

    class Net(nn.Module):          # identical to train_gru.py
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

    seq = SEQ[a.dataset]; static = [f for f in feats if f not in seq]
    reg_t = [t for t in targets if task_of(df, t) == "reg"]; clf_t = [t for t in targets if task_of(df, t) == "clf"]
    pt = Path(a.results_dir) / f"gru__{a.dataset}.pt"
    if not pt.exists(): raise SystemExit(f"ERROR: {pt} not found. Train first: python train_gru.py --raw_dir data --datasets {a.dataset}")
    net = Net(len(static), len(reg_t), len(clf_t), a.hidden)
    net.load_state_dict(torch.load(pt, map_location="cpu")); net.eval()
    j = clf_t.index(a.target); out = {}
    for s, d in splits(df).items():
        xs = torch.tensor(d[seq].to_numpy(), dtype=torch.float32)[..., None]
        xt = torch.tensor(d[static].to_numpy(), dtype=torch.float32)
        with torch.no_grad():
            out[s] = np.concatenate([torch.sigmoid(net(xs[i:i + 4096], xt[i:i + 4096])[1])[:, j].numpy()
                                     for i in range(0, len(xs), 4096)])
    return out


def probs_sklearn(a, df, feats):
    import joblib
    pt = Path(a.results_dir) / "models" / f"{a.model}__{a.dataset}__{a.target}.joblib"
    if not pt.exists(): raise SystemExit(f"ERROR: {pt} not found. Train first: python train_{a.model}.py --raw_dir data --datasets {a.dataset}")
    m = joblib.load(pt)
    return {s: m.predict_proba(d[feats])[:, 1] for s, d in splits(df).items()}


def counts(y, p, thr):
    yh = p >= thr; tp = int((yh & (y == 1)).sum()); fp = int((yh & (y == 0)).sum()); fn = int((~yh & (y == 1)).sum())
    pr, rc = tp / max(1, tp + fp), tp / max(1, tp + fn)
    return dict(threshold=round(float(thr), 3), precision=pr, recall=rc, F1=2 * pr * rc / max(1e-9, pr + rc),
                alarms=int(yh.sum()), true_hits=tp, false_alarms=fp, missed=fn,
                false_per_true=fp / tp if tp else float("nan"))


def main():
    a = ap.parse_args(); a.datasets = [a.dataset]
    prepare(a)
    df, feats, targets, sc = load(a, a.dataset)
    if a.target not in targets or task_of(df, a.target) != "clf":
        raise SystemExit(f"ERROR: {a.target} is not a yes/no target of {a.dataset}. Choices: {[t for t in targets if task_of(df, t) == 'clf']}")
    from common import load_preds
    pr = load_preds(a.results_dir, a.model, a.dataset)
    if pr is not None and f"{a.target}__val" in pr:           # saved predictions (no torch / no retraining needed)
        P = {s_: pr[f"{a.target}__{s_}"].astype(float) for s_ in ("val", "test")}
    else:
        P = probs_gru(a, df, feats, targets) if a.model == "gru" else probs_sklearn(a, df, feats)
    S = splits(df); y = {s: S[s][a.target].to_numpy() for s in S}
    print(f"\n{a.model} | {a.dataset} | {a.target}")
    for s in ("val", "test"):
        print(f"  {s}: {len(y[s])} rows, {int(y[s].sum())} events ({y[s].mean():.1%})")
    if y["test"].sum() < 100:
        print("  WARNING: fewer than 100 events in test -> precision/recall are noisy, treat as rough.")

    grid = sorted(set(np.round(np.arange(0.05, 1.0, 0.05), 3)) | {0.975, 0.99})
    rows = [dict(split=s, **counts(y[s], P[s], t)) for s in ("val", "test") for t in grid]
    tab = pd.DataFrame(rows)
    print("\nTEST split, every threshold (rows with no alarms hidden):")
    show = tab[(tab.split == "test") & (tab.alarms > 0)].drop(columns="split")
    print(show.round(3).to_string(index=False))

    print("\nPick threshold on VAL for a recall target, then measure on TEST (honest number):")
    pick = []
    for r in (0.5, 0.6, 0.7, 0.8, 0.9, 0.95):
        thr = choose_threshold(y["val"], P["val"], r)
        pick.append(dict(val_recall_target=r, **counts(y["test"], P["test"], thr)))
    thr_f1 = choose_threshold(y["val"], P["val"], 0.0)
    pick.append(dict(val_recall_target="best F1", **counts(y["test"], P["test"], thr_f1)))
    print(pd.DataFrame(pick).round(3).to_string(index=False))

    out = Path(a.results_dir); out.mkdir(exist_ok=True)
    f = out / f"sweep_{a.model}_{a.dataset}_{a.target}.csv"
    tab.to_csv(f, index=False); print(f"\nsaved {f}")
    print("Reading it: pick the row whose precision / recall trade-off you accept. 'false_per_true' = false alarms per real event.")


if __name__ == "__main__":
    main()
