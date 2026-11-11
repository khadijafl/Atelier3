"""Charge le modèle sauvegardé et prédit pour une livraison."""
import json
from pathlib import Path

import joblib
import pandas as pd

from logiai.config import ALERT_THRESHOLD, FEATURES, INFO_PATH, MODEL_PATH


class Predictor:
    def __init__(self, model_path: Path = MODEL_PATH, info_path: Path = INFO_PATH):
        self.model = joblib.load(model_path)
        info = {}
        if Path(info_path).exists():
            info = json.loads(Path(info_path).read_text(encoding="utf-8"))
        self.version = info.get("version", "inconnue")
        self.threshold = info.get("seuil", ALERT_THRESHOLD)

    def predict(self, features: dict) -> dict:
        """features : un dictionnaire avec les 7 variables du contrat."""
        df = pd.DataFrame([features], columns=FEATURES)
        proba = float(self.model.predict_proba(df)[0, 1])
        return {
            "probabilite_retard": round(proba, 4),
            "alerte": proba >= self.threshold,
            "seuil": self.threshold,
            "model_version": self.version,
        }
