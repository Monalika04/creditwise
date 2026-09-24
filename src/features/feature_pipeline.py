import pandas as pd
import numpy as np


def prepare_features(df):
    """
    Apply the exact feature engineering used for CreditWise ML.
    Target and metadata columns are removed.
    """

    X = df.copy()

    # Remove target, leakage and metadata
    exclude_cols = [
        "approved",
        "model_target_approval",
        "applicant_id",
        "synthetic_enrichment",
        "synthetic_version"
    ]

    X = X.drop(
        columns=exclude_cols,
        errors="ignore"
    )

    # Remove analytics-only band features
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

    # Date features
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

    # Financial features
    X["dti_percent"] = (
        X["debt_to_income_ratio"] * 100
    )

    X["utilization_percent"] = (
        X["credit_utilization_ratio"] * 100
    )

    X["requested_limit_to_income"] = (
        X["requested_credit_limit"]
        / X["annual_income"].replace(0, np.nan)
    )

    X["disposable_income_ratio"] = (
        X["disposable_income"]
        / X["monthly_income"].replace(0, np.nan)
    )

    X["exposure_to_income"] = (
        X["total_credit_exposure"]
        / X["annual_income"].replace(0, np.nan)
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

    return X