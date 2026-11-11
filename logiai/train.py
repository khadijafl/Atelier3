"""Entraîne le modèle et le sauvegarde : python -m logiai.train"""
import json

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from logiai.config import (ALERT_THRESHOLD, CAT_FEATURES, DATA_PATH, FEATURES, INFO_PATH,
                           MODEL_PATH, NUM_FEATURES, SEED, TARGET)


def train() -> dict:
    df = pd.read_csv(DATA_PATH)
    X, y = df[FEATURES], df[TARGET]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=SEED, stratify=y)

    pre = ColumnTransformer([
        ("num", StandardScaler(), NUM_FEATURES),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CAT_FEATURES),
    ])
    model = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=1000))])
    model.fit(X_tr, y_tr)

    proba = model.predict_proba(X_te)[:, 1]
    pred = (proba >= ALERT_THRESHOLD).astype(int)
    metrics = {
        "baseline_accuracy": round(1 - float(y_te.mean()), 3),
        "accuracy": round(accuracy_score(y_te, pred), 3),
        "rappel": round(recall_score(y_te, pred), 3),
        "precision": round(precision_score(y_te, pred), 3),
        "auc": round(roc_auc_score(y_te, proba), 3),
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    info = {"version": "1.0", "features": FEATURES, "cible": TARGET,
            "seuil": ALERT_THRESHOLD, "metriques": metrics}
    INFO_PATH.write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
    return metrics


if __name__ == "__main__":
    for nom, valeur in train().items():
        print(f"{nom:>18} : {valeur}")
