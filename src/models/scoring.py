import joblib
import os

from src.features.feature_pipeline import prepare_features


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


def load_model():

    return joblib.load(
        os.path.join(
            OUTPUT_DIR,
            "final_model.pkl"
        )
    )


def load_preprocessor():

    return joblib.load(
        os.path.join(
            OUTPUT_DIR,
            "preprocessor.pkl"
        )
    )


def score_applicant(applicant_df):

    model = load_model()
    preprocessor = load_preprocessor()

    features = prepare_features(
        applicant_df
    )

    processed_features = (
        preprocessor.transform(features)
    )

    probability = model.predict_proba(
        processed_features
    )[:, 1][0]

    prediction = model.predict(
        processed_features
    )[0]

    return prediction, probability, processed_features