"""Cross-validation BY PATIENT (GroupKFold) with fixed LightGBM settings -> mean +/- std over folds.
Shows how stable the result is (one val/test split can be lucky or unlucky).
  python cv_report.py --raw_dir data --datasets cgm_t1dm_t2dm --targets target_cgm_t30 target_hypo_60 --folds 5
  python cv_report.py --raw_dir data --datasets ohhim --folds 6      (6 patients = leave-one-patient-out)"""
import argparse
import lightgbm as lgb
import numpy as np, pandas as pd
from sklearn.metrics import average_precision_score, mean_squared_error, roc_auc_score
from sklearn.model_selection import GroupKFold, StratifiedKFold
from common import add_args, load, prepare, task_of

GROUP = {"glucotwin": "Participant_ID", "cgm_t1dm_t2dm": "patient_uid", "ohhim": "patient"}
ap = add_args(argparse.ArgumentParser())
ap.add_argument("--folds", type=int, default=5)
a = ap.parse_args(); prepare(a)
rows = []
for name in a.datasets:
    df, feats, targets, sc = load(a, name)
    for t in (a.targets or targets):
        if t not in targets: continue
        task = task_of(df, t)
        if name in GROUP:
            g = df[GROUP[name]]; folds = list(GroupKFold(n_splits=min(a.folds, g.nunique())).split(df, groups=g))
        else:
            folds = list(StratifiedKFold(a.folds, shuffle=True, random_state=a.seed).split(df, df[t]))
        for k, (tr, te) in enumerate(folds):
            kw = dict(n_estimators=400, learning_rate=0.05, num_leaves=31, subsample=0.8, subsample_freq=1,
                      colsample_bytree=0.8, random_state=a.seed, n_jobs=a.n_jobs, verbose=-1)
            ytr, yte = df[t].iloc[tr], df[t].iloc[te]
            if task == "reg":
                m = lgb.LGBMRegressor(**kw).fit(df[feats].iloc[tr], ytr)
                rows.append(dict(dataset=name, target=t, fold=k, RMSE=float(np.sqrt(mean_squared_error(yte, m.predict(df[feats].iloc[te]))))))
            else:
                pos = ytr.mean(); m = lgb.LGBMClassifier(scale_pos_weight=(1 - pos) / max(pos, 1e-6), **kw).fit(df[feats].iloc[tr], ytr)
                p = m.predict_proba(df[feats].iloc[te])[:, 1]; ok = yte.nunique() > 1
                rows.append(dict(dataset=name, target=t, fold=k, AUC=roc_auc_score(yte, p) if ok else np.nan,
                                 PR_AUC=average_precision_score(yte, p) if ok else np.nan))
        print("done", name, t, flush=True)
out = pd.DataFrame(rows); out.to_csv(f"{a.results_dir}/cv_folds.csv", index=False)
summ = out.groupby(["dataset", "target"]).agg(["mean", "std"]).drop(columns="fold").round(3)
summ.columns = [f"{m}_{s}" for m, s in summ.columns]
summ = summ.dropna(axis=1, how="all"); summ.to_csv(f"{a.results_dir}/cv_summary.csv")
print("\nPER-FOLD results (each fold = unseen patients):"); print(out.round(3).to_string(index=False))
print("\nMEAN and STD over folds (small std = stable result):"); print(summ.to_string())
