import os
import joblib
import pandas as pd
import shap

from src.features.feature_pipeline import prepare_features


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "data",
    "outputs"
)


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():

    return joblib.load(
        os.path.join(
            OUTPUT_DIR,
            "final_model.pkl"
        )
    )


# ============================================================
# LOAD PREPROCESSOR
# ============================================================

def load_preprocessor():

    return joblib.load(
        os.path.join(
            OUTPUT_DIR,
            "preprocessor.pkl"
        )
    )


# ============================================================
# LOAD SHAP BACKGROUND
# ============================================================

def load_shap_background():

    background = joblib.load(
        os.path.join(
            OUTPUT_DIR,
            "X_test_processed.pkl"
        )
    )

    feature_names = joblib.load(
        os.path.join(
            OUTPUT_DIR,
            "feature_names.pkl"
        )
    )

    background_df = pd.DataFrame(
        background,
        columns=feature_names
    )

    return background_df


# ============================================================
# EXPLAIN APPLICANT
# ============================================================

def explain_applicant(applicant_df):

    # Load model
    model = load_model()

    # Load preprocessor
    preprocessor = load_preprocessor()

    # Prepare applicant features
    features = prepare_features(
        applicant_df
    )

    # Transform applicant
    processed = preprocessor.transform(
        features
    )

    # Feature names
    feature_names = (
        preprocessor
        .get_feature_names_out()
    )

    applicant_processed_df = pd.DataFrame(
        processed,
        columns=feature_names
    )

    # --------------------------------------------------------
    # IMPORTANT:
    # Use X_test as SHAP background,
    # NOT the applicant itself.
    # --------------------------------------------------------

    background_df = load_shap_background()

    # Make sure column order matches
    background_df = background_df[
        feature_names
    ]

    # --------------------------------------------------------
    # SHAP Linear Explainer
    # --------------------------------------------------------

    explainer = shap.LinearExplainer(
        model,
        background_df
    )

    shap_values = explainer.shap_values(
        applicant_processed_df
    )

    # First applicant
    values = shap_values[0]

    # --------------------------------------------------------
    # Create result
    # --------------------------------------------------------

    explanation = pd.DataFrame({
        "feature": feature_names,
        "shap_value": values
    })

    explanation["abs_shap"] = (
        explanation["shap_value"]
        .abs()
    )

    explanation = (
        explanation
        .sort_values(
            "abs_shap",
            ascending=False
        )
        .reset_index(drop=True)
    )

    return explanation