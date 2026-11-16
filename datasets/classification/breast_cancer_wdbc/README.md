# Breast Cancer Wisconsin (Diagnostic) — WDBC

- Task: binary classification
- Target column: `diagnosis`
- Target values: `B` = benign; `M` = malignant
- Records: 569
- Predictive features: 30 numeric measurements
- Data file: `breast_cancer_wdbc.csv`
- Original source: [UCI Machine Learning Repository — Breast Cancer Wisconsin (Diagnostic)](https://archive.ics.uci.edu/dataset/17/breast-cancer-wisconsin-diagnostic)
- DOI: https://doi.org/10.24432/C5DW2B
- License: CC BY 4.0

## CSV representation

The CSV contains 31 columns: `diagnosis` followed by the 30 numeric features. The original UCI `ID` identifier column is intentionally omitted because it is not a predictive feature. The feature values come from the scikit-learn packaged copy of the UCI dataset; the encoded target was mapped back to the original UCI labels (`0` → `M`, `1` → `B`).

There are 357 benign records and 212 malignant records. The dataset has no missing feature values.

The `_READY` marker indicates that this dataset folder is complete and may be processed by the automation workflow.
