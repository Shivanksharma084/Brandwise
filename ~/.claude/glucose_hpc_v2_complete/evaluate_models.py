"""Compare models and ENSEMBLE them (average of saved predictions), optional probability calibration.
Run the models first (each saves results/preds/<model>__<dataset>.npz), then:
  python evaluate_models.py --raw_dir data --dataset cgm_t1dm_t2dm --models gru lgbm xgb
  python evaluate_models.py --raw_dir data --dataset ohhim --models lgbm xgb rf --calibrate --min_recall 0.8
Ensemble predictions are saved as model 'ensemble' (or 'ensemble_cal') so sweep_threshold.py can use them."""
import argparse
import numpy as np, pandas as pd
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import brier_score_loss
from common import add_args, choose_threshold, evaluate, is_glucose, load, load_preds, prepare, save_preds, splits, task_of

ap = add_args(argparse.ArgumentParser())
ap.add_argument("--dataset", required=True, choices=["smart_wearable", "glucotwin", "cgm_t1dm_t2dm", "ohhim"])
ap.add_argument("--models", nargs="+", required=True, help="e.g. gru lgbm xgb rf linear")
ap.add_argument("--calibrate", action="store_true", help="isotonic calibration of probabilities (fit on val)")
a = ap.parse_args(); a.datasets = [a.dataset]
prepare(a)
df, feats, targets, sc = load(a, a.dataset); S = splits(df)
P = {m: load_preds(a.results_dir, m, a.dataset) for m in a.models}
bad = [m for m, v in P.items() if v is None]
if bad: raise SystemExit(f"ERROR: no saved predictions for {bad}. Train them first, e.g. python train_{bad[0]}.py --raw_dir data --datasets {a.dataset}")

reg_rows, clf_rows, ens = [], [], {}
for t in (a.targets or targets):
    if t not in targets: continue
    task = task_of(df, t); have = [m for m in a.models if f"{t}__val" in P[m]]
    if not have: continue
    yv, yt = S["val"][t].to_numpy(), S["test"][t].to_numpy()
    pv = {m: P[m][f"{t}__val"].astype(float) for m in have}; pt = {m: P[m][f"{t}__test"].astype(float) for m in have}
    if task == "clf" and a.calibrate:
        for m in have:
            iso = IsotonicRegression(out_of_bounds="clip").fit(pv[m], yv); pv[m], pt[m] = iso.transform(pv[m]), iso.transform(pt[m])
    if len(have) > 1:
        pv["ENSEMBLE"] = np.mean([pv[m] for m in have], 0); pt["ENSEMBLE"] = np.mean([pt[m] for m in have], 0)
        ens[f"{t}__val"], ens[f"{t}__test"] = pv["ENSEMBLE"], pt["ENSEMBLE"]
    for m in pv:
        if task == "reg":
            reg_rows.append(dict(target=t, model=m, **evaluate("reg", yt, pt[m], glucose=is_glucose(t))))
        else:
            thr = choose_threshold(yv, pv[m], a.min_recall)
            clf_rows.append(dict(target=t, model=m, **evaluate("clf", yt, pt[m], thr), Brier=float(brier_score_loss(yt, pt[m]))))
res = a.results_dir
if reg_rows:
    r = pd.DataFrame(reg_rows); r.to_csv(f"{res}/ensemble_{a.dataset}_regression.csv", index=False)
    print("\nREGRESSION - test split (lower RMSE / MAE / MARD = better; higher W15, Clarke = better)")
    print(r.round(3).to_string(index=False))
if clf_rows:
    c = pd.DataFrame(clf_rows); c.to_csv(f"{res}/ensemble_{a.dataset}_classification.csv", index=False)
    print(f"\nCLASSIFICATION - test split, threshold chosen on val ({'min_recall ' + str(a.min_recall) if a.min_recall else 'best F1'}"
          f"{', calibrated' if a.calibrate else ''}; Brier: lower = better calibrated)")
    print(c.round(3).to_string(index=False))
if ens:
    save_preds(res, "ensemble_cal" if a.calibrate else "ensemble", a.dataset, ens)
    print(f"\nensemble saved -> python sweep_threshold.py --raw_dir {a.raw_dir} --dataset {a.dataset} --model {'ensemble_cal' if a.calibrate else 'ensemble'}")
