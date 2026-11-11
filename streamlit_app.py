import requests
import streamlit as st

API_URL = "http://localhost:8000/v1/predict"

st.title("LogiAI : risque de retard")
gauche, droite = st.columns(2)
with gauche:
    distance = st.slider("Distance (km)", 1, 800, 120)
    poids = st.slider("Poids (kg)", 1, 3000, 450)
    heure = st.slider("Heure de départ", 0, 23, 17)
    vehicule = st.selectbox("Véhicule", ["moto", "fourgon", "camion"], index=2)
with droite:
    pluie = st.slider("Pluie (mm)", 0.0, 60.0, 8.0)
    trafic = st.slider("Trafic (0 à 10)", 0.0, 10.0, 7.5)
    arrets = st.slider("Nombre d'arrêts", 0, 12, 4)

if st.button("Évaluer"):
    livraison = {
        "distance_km": distance, "poids_kg": poids, "heure_depart": heure,
        "pluie_mm": pluie, "trafic_index": trafic, "nb_arrets": arrets,
        "type_vehicule": vehicule,
    }
    try:
        r = requests.post(API_URL, json=livraison, timeout=5)
    except requests.ConnectionError:
        st.error("API injoignable : lancez uvicorn dans un autre terminal.")
    else:
        if r.status_code == 200:
            data = r.json()
            st.metric("Probabilité de retard", f"{data['probabilite_retard']:.1%}")
            if data["alerte"]:
                st.warning("Alerte : livraison à risque.")
            else:
                st.success("Livraison probablement à l'heure.")
        else:
            st.error(f"Erreur {r.status_code}")
            st.json(r.json())