# GlucoTwin System Architecture

## Overview

This document describes the system architecture for the GlucoTwin multi-model glucose prediction pipeline. A detailed visual diagram is available in `/docs/GlucoTwin_Architecture_Diagram.pdf`.

## System Components

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
```

## Component Details

### 1. Data Layer

| Source | Type | Format | Frequency |
|--------|------|--------|-----------|
| Dexcom CGM | Continuous Glucose Monitor | API/CSV | Every 5 min |
| Wearable Data | Smartwatch/Band | API/CSV | Every 1-5 min |
| Meal Logs | User Input | Form/API | Per meal |
| Insulin Records | User Input | Form/API | Per dose |

### 2. Ingestion Layer

- **Data Validation:** Schema checks for required fields
- **Timestamp Sync:** All data converted to UTC
- **Missing Value Handling:** Forward-fill for gaps < 30 min
- **Duplicate Removal:** Based on timestamp + source

### 3. Feature Layer

#### Sliding Window Features
- Window sizes: 15 min, 30 min, 60 min, 2 hours
- Aggregations: mean, std, min, max, range

#### Time Encoding
```python
# Cyclical encoding for time of day
hour_sin = sin(2 * π * hour / 24)
hour_cos = cos(2 * π * hour / 24)
```

#### Derived Features
- Rate of change (first derivative)
- Acceleration (second derivative)
- Time since last meal
- Time since last insulin dose

### 4. Model Layer

| Model | Library | Task Type | Output |
|-------|---------|-----------|--------|
| Ridge Regression | sklearn | Regression | glucose prediction |
| Random Forest | sklearn | Regression | glucose prediction |
| LightGBM | lightgbm | Regression/Classification | glucose/hypo |
| XGBoost | xgboost | Regression/Classification | glucose/hypo |
| GRU | TensorFlow | Regression | glucose prediction |

### 5. Ensemble Layer

- **Calibration:** Isotonic Regression on validation set
- **Weighting:** Optimized weights (LGBM: 0.3, XGB: 0.3, Linear: 0.2, GRU: 0.2)
- **Threshold Sweep:** Tested 0.05 to 0.75 for hypoglycemia

### 6. Output Layer

| Output | Format | Update Frequency |
|--------|--------|------------------|
| Glucose Forecast | Numeric + Chart | Every 15 min |
| Hypo Alert | Boolean + Confidence | Every 15 min |
| Confidence Bounds | ±RMSE | Every 15 min |

## Data Flow

1. Raw data ingestion (CSV/API)
2. Data cleaning and validation
3. Feature engineering
4. Model inference (5 parallel models)
5. Ensemble averaging
6. Calibration
7. Output to dashboard

## API Endpoints (Future)

| Endpoint | Method | Description |
|----------|--------|-------------|
| /predict | POST | Get glucose prediction |
| /status | GET | System health check |
| /data/upload | POST | Upload new data |
| /model/info | GET | Model metadata |

## Security Considerations

- Data encrypted at rest (AES-256)
- HTTPS for all API calls
- No PHI stored in logs
- GDPR compliant data handling (future)

---

*For detailed PPT diagram, see `/docs/GlucoTwin_Architecture_Diagram.pdf`*