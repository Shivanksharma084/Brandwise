/* ============================================================
   Glucose HPC v2 — Dashboard JavaScript
   Data loaded from the project's results/ directory
   ============================================================ */

/* ------------------------------------------------------------
   Data extracted from results/ CSV files (hardcoded from files)
   ------------------------------------------------------------ */
const DATASETS = ["smart_wearable", "glucotwin", "cgm_t1dm_t2dm", "ohhim"];

// Regression metrics (RMSE) - lower is better
const regressionRMSE = {
  smart_wearable: { linear: null, lgbm: null, xgb: null }, // only classification
  glucotwin: {
    linear: { t30: 9.056, t60: 23.256, t90: 30.247, t120: 27.989 },
    lgbm:  { t30: 8.516, t60: 19.835, t90: 24.147, t120: 20.695 },
    xgb:   { t30: 8.613, t60: 19.851, t90: 24.002, t120: 21.224 }
  },
  cgm_t1dm_t2dm: {
    linear: { t30: 13.603, t60: 24.529 },
    lgbm:  { t30: 13.238, t60: 23.372 },
    xgb:   { t30: 13.217, t60: 23.750 }
  },
  ohhim: {
    linear: { t30: 25.376, t60: 36.341 },
    lgbm:  { t30: 24.249, t60: 34.239 },
    xgb:   { t30: 23.981, t60: 33.868 }
  }
};

// Classification metrics (AUC / F1) - higher is better
const classificationAUC = {
  smart_wearable: {
    linear: { auc: 0.871, f1: 0.758, accuracy: 0.787 },
    lgbm:  { auc: 0.849, f1: 0.736, accuracy: 0.747 },
    xgb:   { auc: 0.844, f1: 0.735, accuracy: 0.740 }
  },
  cgm_t1dm_t2dm: {
    linear: { auc: 0.982, f1: 0.814 },
    lgbm:  { auc: 0.980, f1: 0.813 },
    xgb:   { auc: 0.983, f1: 0.814 }
  },
  ohhim: {
    linear: { auc: 0.974, f1: 0.302, recall: 1.000 },
    lgbm:  { auc: 0.976, f1: 0.610, recall: 0.662 },
    xgb:   { auc: 0.984, f1: 0.531, recall: 0.479 },
    ensemble: { auc: 0.984, f1: 0.607, recall: 0.859 }
  }
};

// Threshold sweep data (test split, ensemble calibrated)
const thresholdSweep = [
  { thr: 0.05, prec: 0.105, rec: 1.000, f1: 0.190 },
  { thr: 0.10, prec: 0.134, rec: 1.000, f1: 0.237 },
  { thr: 0.15, prec: 0.183, rec: 1.000, f1: 0.309 },
  { thr: 0.20, prec: 0.260, rec: 1.000, f1: 0.413 },
  { thr: 0.25, prec: 0.404, rec: 0.915, f1: 0.560 },
  { thr: 0.30, prec: 0.424, rec: 0.859, f1: 0.567 },
  { thr: 0.35, prec: 0.505, rec: 0.718, f1: 0.593 },
  { thr: 0.40, prec: 0.560, rec: 0.662, f1: 0.606 },
  { thr: 0.45, prec: 0.588, rec: 0.662, f1: 0.623 },
  { thr: 0.50, prec: 0.611, rec: 0.620, f1: 0.615 },
  { thr: 0.55, prec: 0.548, rec: 0.479, f1: 0.511 },
  { thr: 0.60, prec: 0.612, rec: 0.423, f1: 0.500 },
  { thr: 0.65, prec: 0.625, rec: 0.423, f1: 0.504 },
  { thr: 0.70, prec: 0.700, rec: 0.394, f1: 0.505 },
  { thr: 0.75, prec: 0.757, rec: 0.394, f1: 0.518 },
];

/* ------------------------------------------------------------
   Chart 1 — Model Performance Radar / Bar
   ------------------------------------------------------------ */
function initModelChart() {
  const ctx = document.getElementById('chart-models').getContext('2d');

  // Build grouped bar chart: RMSE for regression datasets
  // And AUC for classification dataset
  // Using LGBM results as the primary reference

  const datasets = [
    { label: "LGBM (Glucotwin t+30 RMSE)", data: [8.516], bgColor: "rgba(242,142,43,0.75)", borderColor: "#F28E2B" },
    { label: "XGB (Glucotwin t+30 RMSE)",  data: [8.613], bgColor: "rgba(225,87,89,0.75)",  borderColor: "#E15759" },
    { label: "Linear (Glucotwin t+30 RMSE)", data: [9.056], bgColor: "rgba(78,121,167,0.6)", borderColor: "#4E79A7" },
    { label: "LGBM (Smart Wearable AUC)",  data: [0.849], bgColor: "rgba(242,142,43,0.75)", borderColor: "#F28E2B" },
    { label: "XGB (Smart Wearable AUC)",   data: [0.844], bgColor: "rgba(225,87,89,0.75)",  borderColor: "#E15759" },
    { label: "LGBM (OHIM Hypo AUC)",       data: [0.976], bgColor: "rgba(118,183,178,0.75)", borderColor: "#76B7B2" },
    { label: "XGB (OHIM Hypo AUC)",        data: [0.984], bgColor: "rgba(89,161,79,0.75)", borderColor: "#59A14F" },
  ];

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: [
        "LGBM Glucotwin t+30",
        "XGB Glucotwin t+30",
        "Linear Glucotwin t+30",
        "LGBM Smart AUC",
        "XGB Smart AUC",
        "LGBM OHIM AUC",
        "XGB OHIM AUC",
      ],
      datasets: datasets.map((d, i) => ({
        label: d.label,
        data: d.data,
        backgroundColor: d.bgColor,
        borderColor: d.borderColor,
        borderWidth: 1.5,
        borderRadius: 8,
        barThickness: 24,
      }))
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          backgroundColor: "rgba(10,14,20,0.92)",
          titleColor: "#f0f2f8",
          bodyColor: "#a0a5b8",
          borderColor: "rgba(255,255,255,0.1)",
          borderWidth: 1,
          cornerRadius: 8,
          padding: 12,
          displayColors: true,
        },
        title: {
          display: true,
          text: "LGBM vs XGB vs Linear — Key Metrics (Test Split)",
          color: "#f0f2f8",
          font: { family: "'Inter', sans-serif", size: 16, weight: 700 },
          padding: { bottom: 16 },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: "rgba(255,255,255,0.05)", lineWidth: 0.5 },
          ticks: { color: "#6b6f7e", font: { family: "'JetBrains Mono', monospace", size: 11 } },
          title: { display: true, text: "RMSE (lower = better)  |  AUC (higher = better)", color: "#6b6f7e", font: { size: 11, weight: 600 } },
        },
        x: {
          ticks: { color: "#6b6f7e", font: { family: "'Inter', sans-serif", size: 11 } },
          grid: { display: false },
        },
      },
    }
  });
}

/* ------------------------------------------------------------
   Chart 2 — Threshold Sweep
   ------------------------------------------------------------ */
function initThresholdChart() {
  const ctx = document.getElementById('chart-threshold').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: thresholdSweep.map(d => d.thr.toFixed(2)),
      datasets: [
        {
          label: 'Precision',
          data: thresholdSweep.map(d => d.prec),
          borderColor: "#4E79A7",
          backgroundColor: "rgba(78,121,167,0.15)",
          tension: 0.35,
          pointBackgroundColor: "#4E79A7",
          pointBorderColor: "#fff",
          pointRadius: 4,
          borderWidth: 2.5,
          fill: false,
        },
        {
          label: 'Recall',
          data: thresholdSweep.map(d => d.rec),
          borderColor: "#F28E2B",
          backgroundColor: "rgba(242,142,43,0.15)",
          tension: 0.35,
          pointBackgroundColor: "#F28E2B",
          pointBorderColor: "#fff",
          pointRadius: 4,
          borderWidth: 2.5,
          fill: false,
        },
        {
          label: 'F1 Score',
          data: thresholdSweep.map(d => d.f1),
          borderColor: "#E15759",
          backgroundColor: "rgba(225,87,89,0.15)",
          tension: 0.35,
          pointBackgroundColor: "#E15759",
          pointBorderColor: "#fff",
          pointRadius: 5,
          borderWidth: 3,
          fill: false,
        },
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { intersect: false, mode: 'index' },
      plugins: {
        legend: {
          labels: { color: "#f0f2f8", font: { family: "'Inter', sans-serif", size: 12 }, usePointStyle: true, pointStyle: 'line' },
        },
        tooltip: {
          backgroundColor: "rgba(10,14,20,0.92)",
          titleColor: "#f0f2f8",
          bodyColor: "#a0a5b8",
          borderColor: "rgba(255,255,255,0.1)",
          borderWidth: 1,
          cornerRadius: 8,
          padding: 12,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 1.05,
          grid: { color: "rgba(255,255,255,0.05)", lineWidth: 0.5 },
          ticks: { color: "#6b6f7e", font: { family: "'JetBrains Mono', monospace", size: 11 } },
        },
        x: {
          grid: { display: false },
          ticks: { color: "#6b6f7e", font: { family: "'JetBrains Mono', monospace", size: 10 }, maxRotation: 45 },
        },
      },
    }
  });
}

/* ------------------------------------------------------------
   Init
   ------------------------------------------------------------ */
document.addEventListener('DOMContentLoaded', () => {
  initModelChart();
  initThresholdChart();

  // Subtle entrance animation for cards (CSS handles it, but we add stagger)
  document.querySelectorAll('.card, .kpi-card, .dataset-card').forEach((el, i) => {
    el.style.animationDelay = `${i * 80}ms`;
  });
});
