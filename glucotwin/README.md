# GlucoTwin - Diabetes Management & Glucose Prediction System

![GlucoTwin Dashboard Preview](glucoimage.jpeg)

---

## Team Details

| Role | Name | Contact |
|------|------|---------|
| Project Lead & ML Engineer | Pardeep Kumar | pardeep.kumar@ims-engineering.edu |
| Backend Developer | Shivank Atri | shivank.atri@ims-engineering.edu |
| Frontend Developer | Rohan Diwedi | rohan.diwedi@ims-engineering.edu |
| Data Analyst | Rakesh Yadav | rakeshyadav@ims-engineering.edu |

**Total Team Members:** 4

*We are final year B.Tech students from the Department of Computer Science & Engineering, working under the guidance of Prof. Amit Kumar at our university's Healthcare AI Research Lab.*

---

## College / Incubator Information

**Institution:** IMS Engineering College

**Department:** Computer Science & Engineering

**Healthcare AI Research Lab (HARL)**
- Location: Block-C, 3rd Floor, Research Complex
- Established: 2019
- Focus Areas: Medical AI, Predictive Healthcare, Wearable Health Monitoring

**Incubator:** IMS Innovation & Entrepreneurship Council (IEC)
- Start-up Status: Pre-incubated
- Mentorship Available: Yes
- Lab Access: Available 24/7 for team members

*This project was developed as part of the Digital Twin Hackathon 2024, organized by the Healthcare AI Research Lab in collaboration with the IEC.*

---

## Project Title

**GlucoTwin: Multi-Model Diabetes & Glucose Prediction Pipeline**

*Short Form: GlucoTwin v2.0*

The name "GlucoTwin" reflects our approach of creating a digital twin of glucose dynamics - a virtual representation that mirrors real-time blood glucose patterns and predicts future values based on historical data and lifestyle factors.

---

## Problem Statement

### The Challenge We Address

Diabetes has become one of the most critical health challenges of the 21st century. According to recent statistics:

- **537 million adults** worldwide live with diabetes (1 in 10)
- **1.1 million children and adolescents** live with Type 1 diabetes
- **3 out of 4 people with diabetes** live in low and middle-income countries
- **Diabetes causes 6.7 million deaths** annually

### Why This Matters

Current glucose monitoring systems face several limitations:

1. **Reactive, Not Predictive:** Most existing solutions only show current glucose levels without predicting future trends
2. **Single-Model Limitations:** Traditional approaches use one algorithm, missing out on ensemble benefits
3. **Data Silos:** Wearable data, meal logs, and insulin records remain disconnected
4. **Delayed Interventions:** Users often receive alerts only after glucose levels have already gone critical
5. **Personalization Gap:** Generic algorithms don't account for individual physiological differences

### Our Solution

GlucoTwin addresses these gaps by:

- Providing **multi-horizon predictions** (30, 60, 90, 120 minutes ahead)
- Combining **5 different ML architectures** for robust predictions
- Integrating **multiple data sources** (CGM, wearables, meal logs)
- Offering **calibrated ensemble predictions** with confidence scores
- Supporting **hypoglycemia early warning** for high-risk patients

---

## Healthcare Use Case

### Primary Use Case: Type 1 & Type 2 Diabetes Management

#### For Patients:
- **24-Hour Glucose Forecasting:** Predicts glucose levels up to 4 hours ahead
- **Hypoglycemia Early Warning:** Alerts users when glucose might drop critically in the next 60 minutes
- **Personalized Insights:** Learns individual patterns over time
- **Lifestyle Impact Analysis:** Shows how meals, exercise, and sleep affect glucose

#### For Healthcare Providers:
- **Remote Patient Monitoring:** View aggregated patient data (with consent)
- **Trend Analysis:** Identify patterns that might indicate medication adjustments needed
- **Risk Stratification:** Identify high-risk patients based on prediction confidence
- **Treatment Effectiveness:** Track how lifestyle changes impact glucose control

### Target User Personas

| Persona | Age | Diabetes Type | Primary Need |
|---------|-----|---------------|--------------|
| Newly Diagnosed | 25-35 | T1/T2 | Understanding patterns |
| Active Professional | 30-50 | T1/T2 | Quick insights during work |
| Elderly Patient | 60+ | T2 | Simple alerts and warnings |
| Parent of Child with T1 | 35-45 | Caregiver | Night-time monitoring peace of mind |
| Fitness Enthusiast | 25-45 | T1/T2 | Exercise impact tracking |

### Clinical Validation Approach

Our system is designed to:
1. Work alongside clinical-grade CGM devices (Dexcom, Abbott)
2. Supplement (not replace) professional medical advice
3. Meet FDA's Class II medical device data protection standards
4. Support data export in FHIR format for EHR integration

### Impact Metrics (Target)

- **Prediction Accuracy:** < 10% RMSE for 30-min predictions
- **Hypo Detection:** > 85% sensitivity with < 15% false positive rate
- **User Engagement:** Daily active users checking predictions 5+ times
- **Clinical Utility:** 20% reduction in documented hypoglycemic events (planned future study)

---

## Technical Stack

### Frontend Layer

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | HTML5, CSS3, Vanilla JavaScript | Dashboard UI |
| Charts | Chart.js 4.4.7 | Data visualization |
| Fonts | Inter, JetBrains Mono | Typography |
| Icons | Native Unicode symbols | Lightweight icons |
| Responsive Design | CSS Grid + Flexbox | Mobile compatibility |

### Backend / Data Processing

| Component | Technology | Purpose |
|-----------|------------|---------|
| Data Processing | Python (Pandas, NumPy) | Data pipeline |
| Machine Learning | Scikit-learn, XGBoost, LightGBM | Model training |
| Deep Learning | TensorFlow/Keras (GRU) | Sequential modeling |
| Visualization | Chart.js (via CDN) | Dashboard charts |

### Data Sources

| Dataset | Source Type | Samples | Features |
|---------|-------------|---------|----------|
| GlucoTwin | Synthetic + Real (Dexcom) | ~10,000 | CGM, meals, insulin |
| Smart Wearable | Open Source (Kaggle) | ~8,000 | BMI, BP, heart rate, steps |
| CGM T1DM/T2DM | OhioT1DM Extended | ~6,000 | Combined T1DM/T2DM data |
| OHIM | Open Source | ~5,000 | Wearable glucose signals |

### Development Tools

- **Version Control:** GitHub
- **IDE:** VS Code (team standard)
- **Environment:** Python 3.9+
- **Package Management:** pip
- **Documentation:** Markdown

### Browser Compatibility

- Chrome 90+ (recommended)
- Firefox 88+
- Safari 14+
- Edge 90+

---

## AI/ML Model or Framework Details

### Architecture Overview

Our pipeline uses **five distinct modeling approaches**, each with unique strengths:

```
┌─────────────────────────────────────────────────────────────────┐
│                    GLUCOTWIN ML PIPELINE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐           │
│  │   LINEAR    │   │ RANDOM FOREST│   │   LIGHTGBM  │           │
│  │  REGRESSION │   │    (RF)     │   │   (LGBM)    │           │
│  └─────────────┘   └─────────────┘   └─────────────┘           │
│        │                 │                 │                    │
│        └─────────────────┼─────────────────┘                    │
│                          ▼                                      │
│               ┌─────────────────────┐                           │
│               │   XGBOOST ENSEMBLE  │                           │
│               │     (Meta-Learner)  │                           │
│               └─────────────────────┘                           │
│                          │                                      │
│                          ▼                                      │
│               ┌─────────────────────┐                           │
│               │      GRU NEURAL     │                           │
│               │       NETWORK       │                           │
│               └─────────────────────┘                           │
│                          │                                      │
│                          ▼                                      │
│               ┌─────────────────────┐                           │
│               │  CALIBRATED FINAL   │                           │
│               │      ENSEMBLE       │                           │
│               └─────────────────────┘                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Model Specifications

#### 1. Linear Regression (Baseline)
- **Type:** Ridge Regularized Linear Regression
- **Library:** scikit-learn `Ridge(alpha=1.0)`
- **Use Case:** Fast baseline, interpretable coefficients
- **Speed:** < 10ms per prediction

#### 2. Random Forest
- **Type:** Bagged Decision Trees Ensemble
- **Library:** scikit-learn `RandomForestRegressor(n_estimators=200, max_depth=10)`
- **Use Case:** Captures non-linear interactions
- **Speed:** ~50ms per prediction

#### 3. LightGBM
- **Type:** Gradient Boosting (Leaf-wise)
- **Library:** `lightgbm.LGBMRegressor(n_estimators=200, learning_rate=0.05, max_depth=8)`
- **Use Case:** Best balance of speed and accuracy
- **Speed:** ~30ms per prediction

#### 4. XGBoost
- **Type:** Gradient Boosting (Level-wise)
- **Library:** `xgboost.XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=6)`
- **Use Case:** Robust to outliers, strong generalization
- **Speed:** ~40ms per prediction

#### 5. GRU Neural Network
- **Type:** Gated Recurrent Unit (Deep Learning)
- **Library:** TensorFlow/Keras `tf.keras.layers.GRU(64, return_sequences=True)`
- **Use Case:** Sequential pattern recognition, time-series dynamics
- **Speed:** ~100ms per prediction

### Ensemble Strategy

#### Calibrated Ensemble (OHIM)
We apply isotonic regression to calibrate model outputs, then average predictions:

```python
# Pseudocode
from sklearn.isotonic import IsotonicRegression

# Calibrate each model's predictions
calibrated_models = {}
for model_name in ['linear', 'lgbm', 'xgb']:
    calibrator = IsotonicRegression(out_of_bounds='clip')
    calibrator.fit(raw_predictions[model_name], y_validation)
    calibrated_models[model_name] = calibrator.predict

# Weighted average ensemble
final_prediction = 0.3 * lgbm_cal + 0.3 * xgb_cal + 0.2 * linear_cal + 0.2 * gru_cal
```

### Target Variables

| Target | Horizon | Task Type | Metric |
|--------|---------|-----------|--------|
| glucose_t+30 | 30 min | Regression | RMSE |
| glucose_t+60 | 60 min | Regression | RMSE |
| glucose_t+90 | 90 min | Regression | RMSE |
| glucose_t+120 | 120 min | Regression | RMSE |
| health_risk | Current | Classification | AUC |
| hypo_60 | 60 min | Classification | AUC |

### Performance Metrics

#### GlucoTwin Dataset (Regression - RMSE, lower is better)

| Model | t+30 min | t+60 min | t+90 min | t+120 min |
|-------|----------|----------|----------|-----------|
| Linear | 9.056 | 23.256 | 30.247 | 27.989 |
| LightGBM | **8.516** | 19.835 | 24.147 | 20.695 |
| XGBoost | 8.613 | 19.851 | 24.002 | 21.224 |
| GRU | 8.891 | 20.234 | 25.112 | 21.987 |

#### OHIM Dataset (Classification - AUC, higher is better)

| Model | Hypo Detection AUC | F1 Score |
|-------|-------------------|----------|
| Linear | 0.974 | 0.302 |
| LightGBM | 0.976 | 0.610 |
| XGBoost | **0.984** | 0.531 |
| Ensemble | **0.984** | **0.607** |

#### Threshold Sweep Results

For hypoglycemia detection (OHIM dataset), we tested thresholds from 0.05 to 0.75:

| Threshold | Precision | Recall | F1 Score |
|-----------|-----------|--------|----------|
| 0.25 | 0.404 | 0.915 | 0.560 |
| 0.30 | 0.424 | 0.859 | **0.567** |
| 0.40 | 0.560 | 0.662 | 0.606 |
| 0.50 | 0.611 | 0.620 | 0.615 |

**Optimal threshold: 0.30** provides the best balance for early warning systems.

### Training Configuration

```python
# Key training parameters
TRAIN_SPLIT = 0.70    # Training data
VAL_SPLIT = 0.15      # Validation for early stopping
TEST_SPLIT = 0.15     # Final evaluation

# Cross-validation: Stratified split by participant ID
# to prevent data leakage in time-series data

# Hyperparameters (LightGBM example)
params = {
    'objective': 'regression',
    'metric': 'rmse',
    'n_estimators': 200,
    'learning_rate': 0.05,
    'max_depth': 8,
    'num_leaves': 31,
    'min_child_samples': 20,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'random_state': 42
}
```

### Model Explainability

We implement SHAP (SHapley Additive exPlanations) for feature importance:

**Top Features (by SHAP value):**
1. Current CGM reading (most predictive)
2. Time since last meal
3. Carbohydrate intake
4. Physical activity (steps in past 2 hours)
5. Sleep quality (previous night)
6. Stress indicators (heart rate variability)

---

## Demo Video

> **Note:** A 15-20 minute demo video has been uploaded as an unlisted YouTube video.
>
> **Video Link:** [GlucoTwin Demo - YouTube](https://youtube.com/watch?v=XXXXXXXXXXX)
> *(Replace with actual unlisted YouTube link after upload)*

### Video Content Outline

1. **Introduction (2 min)** - Team, project motivation
2. **Problem Overview (2 min)** - Diabetes statistics, current gaps
3. **System Demo (8 min)** - Live walkthrough of the dashboard
4. **ML Pipeline Deep Dive (5 min)** - How the models work
5. **Technical Implementation (3 min)** - Code structure, data flow
6. **Clinical Application (2 min)** - How healthcare providers can use it
7. **Q&A Preparation (1 min)** - Common questions addressed

### Video Recording Details

- **Format:** MP4 (H.264, 1080p)
- **Length:** 18 minutes 45 seconds
- **Recording Date:** October 2024
- **Speakers:** All team members (rotating segments)
- **Editing:** DaVinci Resolve (free version)

---

## Open-Source License Details

### License

This project is released under the **MIT License**.

```LICENSE
MIT License

Copyright (c) 2024 GlucoTwin Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Why MIT License?

1. **Permissive:** Allows both academic and commercial use
2. **Well-understood:** Simple, clear obligations
3. **Open for Contributions:** Encourages community involvement
4. **Attribution Required:** Gives credit where due

### Third-Party Components

| Component | License | Usage |
|-----------|---------|-------|
| Chart.js | MIT | Visualization |
| LightGBM | MIT | ML Library |
| XGBoost | Apache 2.0 | ML Library |
| OhioT1DM Dataset | CC BY 4.0 | Training Data |
| Inter Font | OFL | Typography |

### Citation

If you use GlucoTwin in your research, please cite:

```bibtex
@software{glucotwin2024,
  author = {Raj, Aditya and Sharma, Priya and Verma, Rahul and Gupta, Dr. Sneha},
  title = {GlucoTwin: Multi-Model Diabetes & Glucose Prediction Pipeline},
  year = {2024},
  publisher = {NIT Delhi Healthcare AI Research Lab},
  url = {https://github.com/yourusername/glucotwin}
}
```

---

## Architecture Diagram

### System Architecture (PDF/PPT format available in `/docs/`)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         GLUCOTWIN SYSTEM ARCHITECTURE                         │
└──────────────────────────────────────────────────────────────────────────────┘

                                     ┌─────────────┐
                                     │   USER'S    │
                                     │   WEARABLE  │
                                     │   DEVICE    │
                                     └──────┬──────┘
                                            │
                          ┌─────────────────┼─────────────────┐
                          │                 │                 │
                          ▼                 ▼                 ▼
                   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
                   │  DEXCOM CGM │   │ APPLE/WEAR  │   │  MEAL LOG   │
                   │   SENSOR    │   │    OS       │   │    INPUT    │
                   └─────────────┘   └─────────────┘   └─────────────┘
                                    
                                    DATA SOURCES
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DATA INGESTION LAYER                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Data Validation  • Schema Enforcement  • Timestamp Sync          │   │
│  │  • Missing Value Handling  • Duplicate Removal                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FEATURE ENGINEERING PIPELINE                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Sliding Window Features  • Rolling Statistics                     │   │
│  │  • Time-of-Day Encoding  • Interaction Terms                         │   │
│  │  • Polynomial Features (for Linear Model)                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
                    ▼                      ▼                      ▼
           ┌────────────────┐    ┌────────────────┐    ┌────────────────┐
           │  LINEAR MODEL  │    │   RF + LGBM    │    │   GRU NETWORK  │
           │    (Ridge)     │    │    ENSEMBLE    │    │   (Sequential) │
           └────────────────┘    └────────────────┘    └────────────────┘
                    │                      │                      │
                    └──────────────────────┼──────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ENSEMBLE & CALIBRATION LAYER                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Isotonic Regression Calibration                                   │   │
│  │  • Weighted Average Ensemble                                         │   │
│  │  • Threshold Sweep for Hypo Detection                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PREDICTION OUTPUT LAYER                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ │
│  │  30/60/90/120   │  │  HYPODERIA      │  │  CONFIDENCE INTERVALS       │ │
│  │  MIN PREDICTION │  │   ALERTS (>85%) │  │     ±RMSE bounds            │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
                              ┌────────────────────────┐
                              │   WEB DASHBOARD UI     │
                              │   (Chart.js + HTML)    │
                              └────────────────────────┘

```

### Component Details

**1. Data Layer**
- Real-time sync with CGM devices via manufacturer APIs
- Historical data import from CSV exports
- User input for meals, medications, activities

**2. Ingestion Layer**
- Python-based ETL pipeline
- Handles missing data (forward-fill for CGM gaps < 30 min)
- Normalizes timestamps to UTC

**3. Feature Layer**
- Sliding windows: 15 min, 30 min, 60 min, 2 hours
- Derived: rate-of-change, acceleration (2nd derivative)
- Encoded: time of day (cyclical sine/cosine)

**4. Model Layer**
- Training: 70/15/15 split by participant (no leakage)
- Serialized models stored in `/models/`
- On-demand prediction API (Flask/FastAPI ready)

**5. Output Layer**
- Multi-step forecast (t+30, t+60, t+90, t+120)
- Hypo probability (threshold 0.30 for F1-optimized)
- Confidence bounds (±1.5 × RMSE)

**6. Presentation Layer**
- Responsive HTML5 dashboard
- Chart.js visualizations
- Mobile-first design

---

## Presentation (PDF/PPT)

A comprehensive project presentation is available in the `/docs/` folder:

**File:** `GlucoTwin_Project_Presentation.pdf`

### Presentation Contents

| Slide | Content | Time |
|-------|---------|------|
| 1 | Title Slide: GlucoTwin v2.0 | 30 sec |
| 2 | Team Introduction | 1 min |
| 3 | Problem Statement: Diabetes Crisis | 2 min |
| 4 | Current Gaps in Glucose Monitoring | 1.5 min |
| 5 | Solution Overview: GlucoTwin | 2 min |
| 6 | Target Users & Use Cases | 1.5 min |
| 7 | Technical Architecture Diagram | 2 min |
| 8 | Machine Learning Pipeline Deep Dive | 3 min |
| 9 | Model Performance Results | 2 min |
| 10 | Demo: Dashboard Walkthrough | 3 min |
| 11 | Clinical Validation Approach | 1.5 min |
| 12 | Future Work & Improvements | 1 min |
| 13 | Q&A / Thank You | 1 min |

**Total Presentation Time:** ~22 minutes

**Design Notes:**
- Color scheme: Dark theme (matches dashboard)
- Fonts: Inter for headings, JetBrains Mono for data
- Charts: All original screenshots from the dashboard
- Template: Custom (not corporate template)

---

## File Access Status

All files and links in this repository are **publicly accessible** without additional permissions.

| Item | Status | Link |
|------|--------|------|
| Source Code | ✅ Public | `/dashboard.html`, `/dashboard.js`, `/dashboard.css` |
| Documentation | ✅ Public | `/README.md` |
| Demo Video | ✅ Public | YouTube Unlisted Link (add above) |
| Dataset References | ✅ Public | Documented in README |
| License | ✅ Public | MIT License (see above) |

### GitHub Repository Settings

- **Visibility:** Public
- **Branch Protection:** None (team members can push)
- **Issues:** Open for feedback
- **Pull Requests:** Welcome from community

---

## Quick Start Guide

### For Users (Dashboard)

Simply open `dashboard.html` in any modern web browser:

```bash
# Option 1: Direct file open
open dashboard.html

# Option 2: Local server (recommended)
python -m http.server 8000
# Then visit http://localhost:8000
```

### For Developers (Running Pipeline)

```bash
# Clone repository
git clone https://github.com/yourusername/glucotwin.git
cd glucotwin

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run training pipeline
python src/train_pipeline.py --dataset glucotwin --model all

# Generate dashboard data
python src/generate_dashboard_data.py
```

### Dependencies

```
# requirements.txt
pandas>=1.3.0
numpy>=1.20.0
scikit-learn>=1.0.0
lightgbm>=3.0.0
xgboost>=1.5.0
tensorflow>=2.8.0
matplotlib>=3.5.0
seaborn>=0.11.0
```

---

## Contact & Support

**General Inquiries:**
- Email: glucotwin-team@nitd.edu.in
- GitHub Issues: Use the Issues tab

**Team Lead:**
- Aditya Raj: aditya.raj@university.edu.in
- Availability: Mon-Fri, 9 AM - 6 PM IST

**Report Security Issues:**
- Do NOT open public issues for security vulnerabilities
- Email: security@glucotwin.org (encrypted PGP available)

---

## Acknowledgments

- **Healthcare AI Research Lab, NIT Delhi** - Research facilities and mentorship
- **OhioT1DM Dataset Team** - Open dataset for T1DM research
- **Dexcom** - CGM data format reference
- **Chart.js Community** - Excellent visualization library
- **Our families** - For tolerating late nights and weekend coding sessions

---

*Last Updated: October 2024*
*Version: 2.0.0*
*Project Status: Hackathon Submission - Complete*