"""Le banc d'essai de l'API. Lancer : python -m pytest"""
from fastapi.testclient import TestClient

from logiai.api.main import app, state

VALIDE = {
    "distance_km": 120.0, "poids_kg": 450.0, "heure_depart": 17,
    "pluie_mm": 8.0, "trafic_index": 7.5, "nb_arrets": 4, "type_vehicule": "camion",
}
DIFFICILE = dict(distance_km=479, poids_kg=2040, heure_depart=17, pluie_mm=46,
                 trafic_index=10, nb_arrets=4, type_vehicule="camion")
FACILE = dict(distance_km=5, poids_kg=3, heure_depart=11, pluie_mm=0,
              trafic_index=1, nb_arrets=0, type_vehicule="moto")

def post(client, **changements):
    return client.post("/v1/predict", json={**VALIDE, **changements})


def test_health_repond_ok():
    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


def test_health_modele_charge():
    with TestClient(app) as client:
        assert client.get("/health").json()["model_loaded"] is True


def test_predict_valide_renvoie_200():
    with TestClient(app) as client:
        assert post(client).status_code == 200


def test_predict_forme_de_la_reponse():
    with TestClient(app) as client:
        data = post(client).json()
        assert set(data) == {"probabilite_retard", "alerte", "seuil", "model_version"}


def test_predict_probabilite_entre_0_et_1():
    with TestClient(app) as client:
        assert 0 <= post(client).json()["probabilite_retard"] <= 1


def test_predict_trajet_risque_plus_eleve_que_trajet_facile():
    facile = dict(distance_km=5, poids_kg=3, heure_depart=11, pluie_mm=0,
                  trafic_index=1, nb_arrets=0, type_vehicule="moto")
    with TestClient(app) as client:
        p_difficile = post(client).json()["probabilite_retard"]
        p_facile = post(client, **facile).json()["probabilite_retard"]
        assert p_difficile > p_facile


def test_distance_negative_refusee():
    with TestClient(app) as client:
        assert post(client, distance_km=-5).status_code == 422


def test_pluie_impossible_refusee():
    with TestClient(app) as client:
        assert post(client, pluie_mm=500).status_code == 422


def test_vehicule_inconnu_refuse():
    with TestClient(app) as client:
        assert post(client, type_vehicule="avion").status_code == 422


def test_champ_manquant_refuse():
    with TestClient(app) as client:
        body = {k: v for k, v in VALIDE.items() if k != "poids_kg"}
        assert client.post("/v1/predict", json=body).status_code == 422


def test_champ_inconnu_refuse():
    with TestClient(app) as client:
        assert post(client, couleur="rouge").status_code == 422


def test_texte_a_la_place_d_un_nombre_refuse():
    with TestClient(app) as client:
        assert post(client, distance_km="loin").status_code == 422


def test_modele_absent_renvoie_503():
    with TestClient(app) as client:
        state.pop("predictor", None)  # on simule un modèle non chargé
        assert post(client).status_code == 503

def test_heure_24_refusee():
    with TestClient(app) as client:
        assert post(client, heure_depart=24).status_code == 422


def test_alerte_coherente_avec_le_seuil():
    with TestClient(app) as client:
        difficile = post(client).json()
        facile = post(client, **FACILE).json()
        assert difficile["alerte"] is True
        assert facile["alerte"] is False

def test_alerte_coherente_avec_le_seuil():
    with TestClient(app) as client:
        assert post(client, **DIFFICILE).json()["alerte"] is True
        assert post(client, **FACILE).json()["alerte"] is False