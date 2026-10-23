"""Shared code for all train_*.py scripts.
Input = your ORIGINAL csv files (GlucoTwin.csv, smart_wearable.csv, t1dm.csv, t2dm.csv, ohhim.csv) in --raw_dir.
First run builds the model-ready data automatically (prep_pipeline.py); later runs reuse it from --processed_dir."""
import argparse
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (average_precision_score, mean_absolute_error, mean_squared_error,
                             precision_recall_curve, roc_auc_score)

# `current` = column with glucose right now (for the "same as now" baseline)
DATASETS = {"smart_wearable": dict(current=None), "glucotwin": dict(current="Dexcom_t0"),
            "cgm_t1dm_t2dm": dict(current="cgm"), "ohhim": dict(current="glucose")}
SEQ = {  # oldest -> newest glucose columns, used by the GRU
    "cgm_t1dm_t2dm": ["cgm_lag_120m", "cgm_lag_90m", "cgm_lag_60m", "cgm_lag_45m", "cgm_lag_30m", "cgm_lag_15m", "cgm"],
    "ohhim": ["glucose_lag_60m", "glucose_lag_45m", "glucose_lag_30m", "glucose_lag_15m", "glucose_lag_10m",
              "glucose_lag_5m", "glucose"]}


def add_args(ap, datasets=None):
    ap.add_argument("--raw_dir", default="data", help="folder with your original csv files")
    ap.add_argument("--processed_dir", default="processed", help="where model-ready data is stored / reused")
    ap.add_argument("--results_dir", default="results")
    ap.add_argument("--rebuild", action="store_true", help="redo data preparation even if processed files exist")
    ap.add_argument("--datasets", nargs="*", default=datasets or list(DATASETS), choices=list(DATASETS))
    ap.add_argument("--targets", nargs="*", help="only these target columns (default: all targets of the dataset)")
    ap.add_argument("--n_jobs", type=int, default=8)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--low_weight", type=float, default=1.0,
                    help="glucose regression: extra weight for samples whose true glucose is below --low_below "
                         "(e.g. 3 = errors near hypo count 3x). 1 = off")
    ap.add_argument("--low_below", type=float, default=90.0)
    ap.add_argument("--min_recall", type=float, default=0.0,
                    help="classification only: 0 = threshold with best F1 on val; e.g. 0.8 = highest-precision "
                         "threshold that still catches >=80%% of events on val")
    return ap


def prepare(a):
    proc = Path(a.processed_dir)
    need = [d for d in a.datasets if a.rebuild or not ((proc / f"{d}_model_ready.csv").exists()
                                                       and (proc / f"schema_{d}.json").exists())]
    if need:
        print(f"preparing data from {a.raw_dir}: {need}", flush=True)
        import prep_pipeline
        prep_pipeline.run_all(a.raw_dir, a.processed_dir, only=need)


def load(a, name):
    df = pd.read_csv(Path(a.processed_dir) / f"{name}_model_ready.csv")
    sc = json.load(open(Path(a.processed_dir) / f"schema_{name}.json"))
    return df, sc["features"], sc["targets"], sc


def task_of(df, t):
    return "clf" if df.loc[df["split"] == "train", t].nunique() <= 2 else "reg"


def splits(df):
    return {s: df[df["split"] == s] for s in ("train", "val", "test")}


def unscale(sc, col, x):
    m, s = sc["scaled_cols_mean_std"][col]
    return x * s + m


def is_glucose(t):
    t = t.lower()
    return ("glucose" in t or "cgm" in t) and "iauc" not in t


def clarke_zones(ref, pred):
    """Clarke Error Grid zone per sample (mg/dL). Returns 0=A, 1-2=B, 3-4=C, 5-6=D, 7-8=E (common reference rules)."""
    a = np.asarray(ref, float); p = np.asarray(pred, float); z = np.full(len(a), -1)

    def put(mask, val):
        m = mask & (z == -1); z[m] = val
    put(((a < 70) & (p < 70)) | (np.abs(a - p) < 0.2 * a), 0)          # A
    put((a <= 70) & (p >= 180), 8)                                       # E (upper left)
    put((a >= 180) & (p <= 70), 7)                                       # E (lower right)
    put((a >= 240) & (p >= 70) & (p <= 180), 6)                          # D (right)
    put((a <= 70) & (p >= 70) & (p <= 180), 5)                           # D (left)
    put((a >= 70) & (a <= 290) & (p >= a + 110), 4)                      # C (upper)
    put((a >= 130) & (a <= 180) & (p <= (7 / 5) * a - 182), 3)           # C (lower)
    put(a < p, 2)                                                        # B (upper)
    put(np.ones(len(a), bool), 1)                                        # B (lower)
    return z


def glucose_extra(y, pred):
    y = np.asarray(y, float); pred = np.asarray(pred, float); z = clarke_zones(y, pred); ok = y > 0
    return dict(MARD=float(np.mean(np.abs(pred[ok] - y[ok]) / y[ok]) * 100),
                W15=float(np.mean(np.abs(pred[ok] - y[ok]) <= 0.15 * y[ok]) * 100),
                Clarke_A=float(np.mean(z == 0) * 100), Clarke_AB=float(np.mean(z <= 2) * 100))


def save_preds(res, model, ds, new):
    """Store val/test predictions (key '<target>__<split>') so models can be ensembled / swept without retraining."""
    d = Path(res) / "preds"; d.mkdir(parents=True, exist_ok=True); f = d / f"{model}__{ds}.npz"
    old = dict(np.load(f)) if f.exists() else {}
    old.update({k: np.asarray(v, dtype=np.float32) for k, v in new.items()})
    np.savez(f, **old)


def load_preds(res, model, ds):
    f = Path(res) / "preds" / f"{model}__{ds}.npz"
    return dict(np.load(f)) if f.exists() else None


def best_f1_threshold(y, p):
    pr, rc, th = precision_recall_curve(y, p)
    f1 = 2 * pr * rc / np.clip(pr + rc, 1e-9, None)
    return float(th[np.argmax(f1[:-1])]) if len(th) else 0.5


def choose_threshold(y, p, min_recall=0.0):
    """Threshold picked on VAL. min_recall>0: best precision among thresholds reaching that recall; else best F1."""
    if min_recall > 0:
        pr, rc, th = precision_recall_curve(y, p)
        ok = np.where(rc[:-1] >= min_recall)[0]
        if len(ok): return float(th[ok[np.argmax(pr[:-1][ok])]])
    return best_f1_threshold(y, p)


def save_metrics(out, res, name):
    """Write all metrics + separate regression / classification tables (no NaN columns), print test results."""
    out.to_csv(res / f"{name}_metrics.csv", index=False)
    kinds = (("regression", ["RMSE", "MAE", "MARD", "W15", "Clarke_A", "Clarke_AB"], "lower RMSE / MAE / MARD = better; higher W15 (% within 15%) and Clarke A/AB (%) = better"),
             ("classification", ["AUC", "PR_AUC", "accuracy", "precision", "recall", "F1", "threshold"],
              "higher AUC / PR_AUC / F1 = better"))
    for kind, cols, hint in kinds:
        sub = out[out[cols[0]].notna()] if cols[0] in out else out.iloc[0:0]
        if sub.empty: continue
        sub = sub[["dataset", "model", "target", "split"] + [x for x in cols if x in sub]]
        sub.to_csv(res / f"{name}_{kind}.csv", index=False)
        print(f"\n{kind.upper()} - test split ({hint})")
        print(sub[sub["split"] == "test"].drop(columns="split").round(3).to_string(index=False))


def evaluate(task, y, pred, thr=None, glucose=False):
    y = np.asarray(y)
    if task == "reg":
        out = dict(RMSE=float(np.sqrt(mean_squared_error(y, pred))), MAE=float(mean_absolute_error(y, pred)))
        if glucose: out.update(glucose_extra(y, pred))
        return out
    ok = len(set(y)) > 1
    out = dict(AUC=float(roc_auc_score(y, pred)) if ok else np.nan,
               PR_AUC=float(average_precision_score(y, pred)) if ok else np.nan)
    if thr is not None:
        yhat = (np.asarray(pred) >= thr).astype(int); tp = int(((yhat == 1) & (y == 1)).sum())
        fp = int(((yhat == 1) & (y == 0)).sum()); fn = int(((yhat == 0) & (y == 1)).sum())
        out.update(accuracy=float((yhat == y).mean()), precision=tp / max(1, tp + fp), recall=tp / max(1, tp + fn),
                   F1=2 * tp / max(1, 2 * tp + fp + fn), threshold=thr)
    return out


def default_fit(m, Xtr, ytr, Xva, yva, w=None):
    m.fit(Xtr, ytr) if w is None else m.fit(Xtr, ytr, sample_weight=w)


def run_tabular(a, model_name, make, fit=None, with_same_as_now=False):
    """Train one sklearn-style model per (dataset, target); write metrics + saved model.
    make(task, pos_weight, args) -> estimator ; fit(model, Xtr, ytr, Xva, yva) optional (early stopping etc.)."""
    prepare(a)
    res = Path(a.results_dir); (res / "models").mkdir(parents=True, exist_ok=True)
    rows = []
    for name in a.datasets:
        df, feats, targets, sc = load(a, name)
        S = splits(df); preds = {}
        for t in (a.targets or targets):
            if t not in targets: continue
            task = task_of(df, t)
            pos = float(S["train"][t].mean()) if task == "clf" else None
            m = make(task, (1 - pos) / max(pos, 1e-6) if pos is not None else None, a)
            w = (np.where(S["train"][t].to_numpy() < a.low_below, a.low_weight, 1.0)
                 if task == "reg" and a.low_weight != 1.0 and is_glucose(t) else None)
            (fit or default_fit)(m, S["train"][feats], S["train"][t], S["val"][feats], S["val"][t], w)
            pv = (lambda d: m.predict(d[feats])) if task == "reg" else (lambda d: m.predict_proba(d[feats])[:, 1])
            thr = choose_threshold(S["val"][t], pv(S["val"]), a.min_recall) if task == "clf" else None
            for s in ("val", "test"):
                rows.append(dict(dataset=name, model=model_name, target=t, split=s,
                                 **evaluate(task, S[s][t], pv(S[s]), thr, glucose=(task == "reg" and is_glucose(t)))))
            preds[f"{t}__val"], preds[f"{t}__test"] = pv(S["val"]), pv(S["test"])
            cur = DATASETS[name]["current"]
            if with_same_as_now and cur and task == "reg" and ("glucose" in t.lower() or "cgm" in t.lower()):
                for s in ("val", "test"):
                    rows.append(dict(dataset=name, model="same-as-now", target=t, split=s,
                                     **evaluate("reg", S[s][t], unscale(sc, cur, S[s][cur].to_numpy()), glucose=True)))
            joblib.dump(m, res / "models" / f"{model_name}__{name}__{t}.joblib")
            print(f"trained {model_name} | {name} | {t}", flush=True)
        save_preds(res, model_name, name, preds)
    out = pd.DataFrame(rows)
    save_metrics(out, res, model_name)
    return out
