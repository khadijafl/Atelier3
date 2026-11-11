"""Réglages du projet LogiAI : tout ce qui peut changer est ici."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "livraisons.csv"
MODEL_PATH = ROOT / "models" / "model.joblib"
INFO_PATH = ROOT / "models" / "model_info.json"

TARGET = "retard"  # 1 = livraison en retard, 0 = à l'heure
NUM_FEATURES = ["distance_km", "poids_kg", "heure_depart", "pluie_mm", "trafic_index", "nb_arrets"]
CAT_FEATURES = ["type_vehicule"]
FEATURES = NUM_FEATURES + CAT_FEATURES

ALERT_THRESHOLD = 0.4  # au-dessus : on prévient le dispatcher
SEED = 42
