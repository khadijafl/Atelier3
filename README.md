# LogiAI : starter du TP (séance API)

Prédire le risque de retard d'une livraison et l'exposer par une API REST (FastAPI).

## Installation (une fois)

    python -m venv .venv
    .venv\Scripts\activate.bat        # Windows cmd  (PowerShell : .venv\Scripts\Activate.ps1)
    source .venv/bin/activate         # macOS / Linux
    pip install -r requirements.txt

## Données et modèle

    python -m logiai.dataset          # écrit data/livraisons.csv
    python -m logiai.train            # écrit models/model.joblib et models/model_info.json

## Lancer l'API

    python -m uvicorn logiai.api.main:app --reload
    # puis http://localhost:8000/docs

## Tests

    python -m pytest

## À écrire par vous

- `logiai/api/schemas.py` : les 6 champs manquants de `Livraison`
- `logiai/api/main.py` : le corps de `predict()`
