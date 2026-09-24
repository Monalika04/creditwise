import os
import joblib
import pandas as pd
import numpy as np

from sklearn import __version__ as sklearn_version
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split


print("Python environment:")
print(sklearn_version)
print()


# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "creditwise_cleaned.csv"
)

OUTPUT_PATH = os.path.join(
    BASE_DIR,
    "data",
    "outputs",
    "preprocessor.pkl"
)


# ============================================================
# 2. LOAD DATA
# ============================================================

df = pd.read_csv(DATA_PATH)

print("Dataset shape:", df.shape)


# ============================================================
# 3. TARGET
# ============================================================

TARGET = "approved"

y = df[TARGET].copy()

X = df.drop(
    columns=[TARGET]
).copy()


# ============================================================
# 4. EXACT MODULE 5 FEATURE ENGINEERING
# ============================================================

exclude_cols = [
    "model_target_approval",
    "applicant_id",
    "synthetic_enrichment",
    "synthetic_version"
]

X = X.drop(
    columns=exclude_cols,
    errors="ignore"
)


band_cols = [
    "income_band",
    "dti_band",
    "credit_history_band",
    "employment_band",
    "payment_risk_indicator"
]

X = X.drop(
    columns=band_cols,
    errors="ignore"
)


X["application_date"] = pd.to_datetime(
    X["application_date"],
    errors="coerce"
)

X["application_year"] = (
    X["application_date"].dt.year
)

X["application_month"] = (
    X["application_date"].dt.month
)


X["dti_percent"] = (
    X["debt_to_income_ratio"] * 100
)

X["utilization_percent"] = (
    X["credit_utilization_ratio"] * 100
)


X["requested_limit_to_income"] = (
    X["requested_credit_limit"]
    /
    X["annual_income"].replace(0, np.nan)
)


X["disposable_income_ratio"] = (
    X["disposable_income"]
    /
    X["monthly_income"].replace(0, np.nan)
)


X["exposure_to_income"] = (
    X["total_credit_exposure"]
    /
    X["annual_income"].replace(0, np.nan)
)


X = X.drop(
    columns=[
        "monthly_income",
        "application_date"
    ],
    errors="ignore"
)


X = X.replace(
    [np.inf, -np.inf],
    np.nan
)


# ============================================================
# 5. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# ============================================================
# 6. FEATURE TYPES
# ============================================================

numeric_features = (
    X_train
    .select_dtypes(
        include=["int64", "float64"]
    )
    .columns
    .tolist()
)

categorical_features = (
    X_train
    .select_dtypes(
        include=["object"]
    )
    .columns
    .tolist()
)


print(
    "Numerical features:",
    len(numeric_features)
)

print(
    "Categorical features:",
    len(categorical_features)
)


# ============================================================
# 7. COMPLETELY NEW PREPROCESSING PIPELINES
# ============================================================

numeric_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(
            strategy="median"
        )
    ),
    (
        "scaler",
        StandardScaler()
    )
])


categorical_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(
            strategy="most_frequent"
        )
    ),
    (
        "onehot",
        OneHotEncoder(
            handle_unknown="ignore",
            sparse_output=False
        )
    )
])


# ============================================================
# 8. NEW COLUMN TRANSFORMER
# ============================================================

preprocessor = ColumnTransformer([
    (
        "num",
        numeric_pipeline,
        numeric_features
    ),
    (
        "cat",
        categorical_pipeline,
        categorical_features
    )
])


# ============================================================
# 9. FIT FROM SCRATCH
# ============================================================

X_train_processed = (
    preprocessor.fit_transform(X_train)
)

X_test_processed = (
    preprocessor.transform(X_test)
)


# ============================================================
# 10. VERIFY
# ============================================================

print()
print(
    "Processed training shape:",
    X_train_processed.shape
)

print(
    "Processed testing shape:",
    X_test_processed.shape
)

print(
    "Feature count:",
    len(
        preprocessor
        .get_feature_names_out()
    )
)


num_imputer = (
    preprocessor
    .named_transformers_["num"]
    .named_steps["imputer"]
)

cat_imputer = (
    preprocessor
    .named_transformers_["cat"]
    .named_steps["imputer"]
)


print()
print(
    "Numeric imputer _fill_dtype:",
    hasattr(
        num_imputer,
        "_fill_dtype"
    )
)

print(
    "Categorical imputer _fill_dtype:",
    hasattr(
        cat_imputer,
        "_fill_dtype"
    )
)


# ============================================================
# 11. SAVE
# ============================================================

os.makedirs(
    os.path.dirname(OUTPUT_PATH),
    exist_ok=True
)

joblib.dump(
    preprocessor,
    OUTPUT_PATH
)


print()
print("Preprocessor saved successfully.")
print()
print("Saved file:")
print(OUTPUT_PATH)