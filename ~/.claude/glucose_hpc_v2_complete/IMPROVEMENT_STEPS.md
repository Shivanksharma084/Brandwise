# All steps to improve accuracy (Windows PowerShell, run inside the glucose_hpc_v2 folder)

## Step 0. Setup (once)
```powershell
cd C:\Users\Administrator\Downloads\glucose_hpc_v2
..\DATASET\.venv\Scripts\Activate.ps1        # or make a new env: python -m venv .venv ; .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
(`data\t2dm.csv` in this zip is already the clean original, no date fix needed.)

## Step 1. Train the classic models. Each one SAVES its predictions.  --low_weight 3 = errors at low glucose count 3x
```powershell
python train_linear.py --raw_dir data --n_jobs 4 --low_weight 3
python train_lgbm.py   --raw_dir data --n_jobs 4 --low_weight 3
python train_xgb.py    --raw_dir data --n_jobs 4 --low_weight 3
python train_rf.py     --raw_dir data --n_jobs 4 --trees 100 --low_weight 3
```
New columns in `results\*_regression.csv`: MARD (%), W15 (% within 15%), Clarke_A, Clarke_AB (%).

## Step 2. GRU v2: 3 seeds averaged + low-glucose weight (slow on laptop: use Kaggle/Colab/college GPU)
```powershell
python train_gru.py --raw_dir data --epochs 60 --seeds 3 --low_weight 3
```
Test first with `--epochs 2 --seeds 1`. If v2 fails, `train_gru_v1.py` is the old working version.

## Step 3. Ensemble + calibration (seconds, no retraining)
```powershell
python evaluate_models.py --raw_dir data --dataset cgm_t1dm_t2dm --models gru lgbm xgb
python evaluate_models.py --raw_dir data --dataset ohhim --models lgbm xgb rf --calibrate
```
`--calibrate` fixes probabilities that do not carry over from val to test (helps ohhim hypo). `--min_recall 0.8` = safety-first threshold.

## Step 4. Threshold table for the ensemble
```powershell
python sweep_threshold.py --raw_dir data --dataset cgm_t1dm_t2dm --model ensemble
python sweep_threshold.py --raw_dir data --dataset ohhim --model ensemble_cal
```

## Step 5. Cross-validation by patient (is the result stable?)
```powershell
python cv_report.py --raw_dir data --datasets cgm_t1dm_t2dm --folds 5
python cv_report.py --raw_dir data --datasets ohhim --folds 6
python cv_report.py --raw_dir data --datasets glucotwin smart_wearable --folds 5
```
Report mean +/- std. A small std means the result is trustworthy.

## Step 6. For the report
- Glucose: RMSE, MAE, MARD, % within 15%, Clarke zone A and A+B.
- Hypo: AUC, PR-AUC, precision, recall, F1 at a threshold chosen on VAL (say which rule).
- State patients and event counts per split (ohhim: 6 patients, 71 test hypo events).

## Not built (need more data or time)
More patients / pre-train on CGM then fine-tune ohhim; per-patient fine-tuning; Transformer / TCN models.
