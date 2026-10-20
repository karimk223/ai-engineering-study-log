from contextlib import asynccontextmanager
from pathlib import Path

import joblib
from fastapi import FastAPI, HTTPException, Path as ApiPath
from pydantic import BaseModel, Field, StrictStr
from app.database import init_database, save_prediction, get_prediction


MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "artifacts"
    / "ticket_router_full_v1.joblib"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not MODEL_PATH.is_file():
        raise RuntimeError("Saved model missing. Run train_model_full.py first.")

    app.state.model_bundle = joblib.load(MODEL_PATH)
    init_database()
    yield


app = FastAPI(title="Ticket Prediction API", lifespan=lifespan)


class PredictionInput(BaseModel):
    message: StrictStr = Field(min_length=1, max_length=2000)

    class Config:
        anystr_strip_whitespace = True
        extra = "forbid"


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_version": app.state.model_bundle["model_version"],
    }


@app.post("/predict")
def predict(payload: PredictionInput):
    bundle = app.state.model_bundle
    model = bundle["pipeline"]

    scores = model.predict_proba([payload.message])[0]
    top_index = int(scores.argmax())
    category = str(model.classes_[top_index])
    score = float(scores[top_index])

    prediction_id = save_prediction(
        payload.message, category, score, bundle["model_version"]
    )

    return {
        "id": prediction_id,
        "category": category,
        "score": score,
        "model_version": bundle["model_version"],
    }

@app.get("/predictions/{prediction_id}")
def read_prediction(
    prediction_id: int = ApiPath(ge=1, le=9_223_372_036_854_775_807),
):
    record = get_prediction(prediction_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return record