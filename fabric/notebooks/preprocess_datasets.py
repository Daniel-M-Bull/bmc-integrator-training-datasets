# Fabric Notebook source: BMC Integrator dataset preprocessing
# Import this script into a Microsoft Fabric Notebook or copy its cells into one.
# Attach BMC_Integrator_Lakehouse as the default lakehouse before running.
#
# Expected input layout:
# Files/raw/classification/<dataset_id>/<file>.csv
# Files/raw/regression/<dataset_id>/<file>.csv
#
# Output:
# Delta tables named curated_<dataset_id> in the attached Lakehouse.
#
# Parameter cell: in Fabric, mark the cell containing dataset_id as a parameter cell
# if you want to override it through the Notebook Job Scheduler API.

# %% [markdown]
# # BMC Integrator — dataset preprocessing
#
# This notebook preserves source files under Files/raw and writes cleaned Delta
# tables to the Lakehouse. It does not train models; Qaptiva remains responsible
# for model execution.

# %%
from pyspark.sql import functions as F
from pyspark.sql import types as T
import json
from datetime import datetime, timezone

# %% [markdown]
# ## Parameters
#
# Set dataset_id to one dataset ID or "all". The default is "all".

# %%
dataset_id = "all"  # "iris", "breast_cancer_wdbc", "wine", "auto_mpg", "boston_housing", "tips", or "all"
raw_root = "Files/raw"

# %%
DATASETS = {
    "iris": {
        "task": "classification",
        "filename": "iris.csv",
        "target": "species",
        "target_type": "classification",
    },
    "breast_cancer_wdbc": {
        "task": "classification",
        "filename": "breast_cancer_wdbc.csv",
        "target": "diagnosis",
        "target_type": "classification",
    },
    "wine": {
        "task": "classification",
        "filename": "wine.csv",
        "target": "class",
        "target_type": "classification",
    },
    "auto_mpg": {
        "task": "regression",
        "filename": "auto_mpg.csv",
        "target": "mpg",
        "target_type": "regression",
    },
    "boston_housing": {
        "task": "regression",
        "filename": "boston_housing.csv",
        "target": "medv",
        "target_type": "regression",
    },
    "tips": {
        "task": "regression",
        "filename": "tips.csv",
        "target": "tip",
        "target_type": "regression",
    },
}

# %%
if dataset_id == "all":
    selected_ids = list(DATASETS.keys())
elif dataset_id in DATASETS:
    selected_ids = [dataset_id]
else:
    raise ValueError(
        f"Unknown dataset_id={dataset_id!r}. Valid values: {', '.join(DATASETS)} or 'all'."
    )

run_started = datetime.now(timezone.utc).isoformat()
run_results = []

# %%
def read_raw_dataset(dataset_key: str):
    meta = DATASETS[dataset_key]
    path = f"{raw_root}/{meta['task']}/{dataset_key}/{meta['filename']}"

    # Auto MPG uses '?' for missing horsepower values. Treat it as null.
    df = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .option("mode", "PERMISSIVE")
        .option("nullValue", "?")
        .option("emptyValue", "")
        .option("quote", '"')
        .option("escape", '"')
        .csv(path)
    )
    return df, path


def preprocess_dataset(dataset_key: str):
    meta = DATASETS[dataset_key]
    df, source_path = read_raw_dataset(dataset_key)

    if len(df.columns) == 0:
        raise ValueError(f"{dataset_key}: no columns found at {source_path}")

    target = meta["target"]
    if target not in df.columns:
        raise ValueError(
            f"{dataset_key}: target column '{target}' not found. "
            f"Columns found: {df.columns}"
        )

    input_rows = df.count()
    if input_rows == 0:
        raise ValueError(f"{dataset_key}: source dataset is empty")

    # Remove duplicate column names, which can make downstream model pipelines ambiguous.
    lowered = [c.lower() for c in df.columns]
    if len(lowered) != len(set(lowered)):
        raise ValueError(f"{dataset_key}: duplicate column names (case-insensitive)")

    # Count missing values before cleaning. The target is never imputed.
    missing_before = {
        c: df.filter(F.col(c).isNull()).count()
        for c in df.columns
    }

    df = df.filter(F.col(target).isNotNull())
    rows_after_target_check = df.count()
    if rows_after_target_check == 0:
        raise ValueError(f"{dataset_key}: every row has a null target '{target}'")

    feature_columns = [c for c in df.columns if c != target]
    numeric_types = (
        T.ByteType, T.ShortType, T.IntegerType, T.LongType,
        T.FloatType, T.DoubleType, T.DecimalType
    )
    numeric_features = [
        field.name for field in df.schema.fields
        if field.name != target and isinstance(field.dataType, numeric_types)
    ]
    categorical_features = [
        c for c in feature_columns if c not in numeric_features
    ]

    # Impute numeric feature nulls with the median and categorical feature nulls
    # with the most frequent value. The target column is deliberately excluded.
    numeric_fill = {}
    for col_name in numeric_features:
        values = df.approxQuantile(col_name, [0.5], 0.01)
        if values:
            numeric_fill[col_name] = float(values[0])

    categorical_fill = {}
    for col_name in categorical_features:
        mode_row = (
            df.filter(F.col(col_name).isNotNull())
              .groupBy(col_name)
              .count()
              .orderBy(F.desc("count"), F.asc(col_name))
              .first()
        )
        if mode_row is not None:
            categorical_fill[col_name] = mode_row[0]

    fill_values = {**numeric_fill, **categorical_fill}
    cleaned = df.fillna(fill_values) if fill_values else df

    # Fail rather than silently write a curated table with missing feature values.
    remaining_missing = {
        c: cleaned.filter(F.col(c).isNull()).count()
        for c in feature_columns
    }
    unresolved = {c: n for c, n in remaining_missing.items() if n > 0}
    if unresolved:
        raise ValueError(
            f"{dataset_key}: missing feature values remain after imputation: {unresolved}"
        )

    output_rows = cleaned.count()
    table_name = f"curated_{dataset_key}"
    (
        cleaned.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(table_name)
    )

    return {
        "dataset_id": dataset_key,
        "task": meta["target_type"],
        "source_path": source_path,
        "target": target,
        "input_rows": input_rows,
        "rows_after_target_check": rows_after_target_check,
        "output_rows": output_rows,
        "columns": len(cleaned.columns),
        "numeric_features_imputed": sorted(numeric_fill.keys()),
        "categorical_features_imputed": sorted(categorical_fill.keys()),
        "missing_before": missing_before,
        "table_name": table_name,
        "status": "SUCCESS",
    }


# %%
for key in selected_ids:
    try:
        result = preprocess_dataset(key)
        run_results.append(result)
        print(json.dumps(result, ensure_ascii=False, default=str))
    except Exception as exc:
        failure = {
            "dataset_id": key,
            "status": "FAILED",
            "error": str(exc),
        }
        run_results.append(failure)
        print(json.dumps(failure, ensure_ascii=False, default=str))
        # Stop the batch on first failure so the orchestrator receives a failed run.
        raise

# %%
summary = {
    "process": "bmc_integrator_preprocessing",
    "started_utc": run_started,
    "finished_utc": datetime.now(timezone.utc).isoformat(),
    "requested_dataset_id": dataset_id,
    "results": run_results,
    "status": "SUCCESS",
}
print(json.dumps(summary, ensure_ascii=False, default=str))

# In Fabric, this JSON summary is visible in notebook output. When we wire the
# Notebook Job Scheduler API to Control-M, we will also capture the job instance
# state and exit value through the API.
