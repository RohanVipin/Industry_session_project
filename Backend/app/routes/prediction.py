from fastapi import APIRouter
import pandas as pd
import joblib
import os

from app.schemas.prediction import PredictionInput
from app.database.mongodb import predictions_collection
from app.utils.retention import recommend, describe_rules
from app.utils.explain import risk_factors


router = APIRouter(
    prefix="/prediction",
    tags=["Prediction"]
)


# Load trained model
BASE_PATH = os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)

MODEL_PATH = os.path.join(
    BASE_PATH,
    "ML",
    "models",
    "churn_model.pkl"
)

model = joblib.load(MODEL_PATH)


@router.get("/rules")
def get_rules():
    """The retention rules and thresholds, so the web page can show them."""
    return describe_rules()


@router.post("/predict")
def predict_churn(data: PredictionInput):

    customer = data.model_dump()

    model_input = pd.DataFrame([
        customer
    ])

    prediction = model.predict(
        model_input
    )[0]

    probability = float(model.predict_proba(
        model_input
    )[0][1])

    if prediction == 1:
        result = "Customer likely to churn"
    else:
        result = "Customer unlikely to churn"

    # Retention recommendation (plain business rules) and score explanation
    retention = recommend(
        probability,
        customer
    )

    factors = risk_factors(model, model_input)

    prediction_record = {
        "prediction": int(prediction),
        "result": result,
        "churn_probability": probability,
        "risk_level": retention["risk_level"],
        "suggested_action": retention["action"],
        "rule": retention["rule"]
    }

    predictions_collection.insert_one(
        prediction_record
    )

    return {
        "prediction": int(prediction),
        "result": result,
        "churn_probability": round(
            probability * 100,
            2
        ),
        "risk_level": retention["risk_level"],
        "risk_factors": factors,
        "retention": retention
    }
