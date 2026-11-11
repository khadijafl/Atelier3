"""L'API LogiAI : python -m uvicorn logiai.api.main:app --reload"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from logiai.api.schemas import Livraison, PredictionOut
from logiai.config import MODEL_PATH
from logiai.predict import Predictor

state: dict = {}  # contient le "predictor" une fois le modèle chargé


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Exécuté UNE fois, au démarrage du serveur (pas à chaque requête)
    if MODEL_PATH.exists():
        state["predictor"] = Predictor(MODEL_PATH)
    yield
    state.clear()


app = FastAPI(
    title="LogiAI",
    version="1.0.0",
    description="Prédit le risque de retard d'une livraison à partir de ses caractéristiques.",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": "predictor" in state}




@app.post("/v1/predict", response_model=PredictionOut)
def predict(livraison: Livraison):
    predictor = state.get("predictor")
    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Modèle non chargé : lancez 'python -m logiai.train' puis relancez le serveur.",
        )
    return PredictionOut(**predictor.predict(livraison.model_dump()))