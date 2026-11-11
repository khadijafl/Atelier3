"""Fabrique un jeu de données synthétique de livraisons : python -m logiai.dataset"""
import numpy as np
import pandas as pd

from logiai.config import DATA_PATH, SEED


def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def make_dataset(n: int = 5000, seed: int = SEED, taux_retard: float = 0.28) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    vehicule = rng.choice(["moto", "fourgon", "camion"], size=n, p=[0.25, 0.50, 0.25])
    distance = np.clip(rng.lognormal(mean=3.6, sigma=0.9, size=n), 2, 800)
    distance = np.where(vehicule == "moto", np.clip(distance, 2, 60), distance)
    poids = np.where(
        vehicule == "moto", rng.uniform(0.5, 15, n),
        np.where(vehicule == "fourgon", rng.uniform(5, 800, n), rng.uniform(300, 3000, n)),
    )
    heure = np.clip(np.round(rng.normal(11, 4, n)), 0, 23).astype(int)
    pluie = np.where(rng.random(n) < 0.6, 0.0, rng.exponential(5, n))
    pluie = np.clip(pluie, 0, 60)
    pic = np.exp(-((heure - 8) ** 2) / 8) + np.exp(-((heure - 17.5) ** 2) / 8)
    trafic = np.clip(2 + 5 * pic + rng.normal(0, 1, n), 0, 10)
    arrets = np.clip(rng.poisson(2.5, n), 0, 12)

    score = (
        0.006 * distance + 0.0006 * poids + 0.35 * trafic + 0.06 * pluie + 0.25 * arrets
        + np.where(vehicule == "moto", -0.4, 0.0) + np.where(vehicule == "camion", 0.5, 0.0)
        + rng.normal(0, 0.6, n)
    )
    # on règle l'intercept pour obtenir environ 28 % de retards
    lo, hi = -20.0, 5.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if _sigmoid(score + mid).mean() > taux_retard:
            hi = mid
        else:
            lo = mid
    retard = (rng.random(n) < _sigmoid(score + mid)).astype(int)

    return pd.DataFrame({
        "distance_km": distance.round(1),
        "poids_kg": poids.round(1),
        "heure_depart": heure,
        "pluie_mm": pluie.round(1),
        "trafic_index": trafic.round(1),
        "nb_arrets": arrets,
        "type_vehicule": vehicule,
        "retard": retard,
    })


if __name__ == "__main__":
    df = make_dataset()
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_PATH, index=False)
    print(f"{len(df)} lignes écrites dans {DATA_PATH} (retards : {df['retard'].mean():.1%})")
