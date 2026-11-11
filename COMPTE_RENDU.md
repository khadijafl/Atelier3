# Compte rendu : TP API LogiAI

**Nom:** Flija  **Groupe :** 4

## 1. Environnement et premiers tests
- Sortie de `python -m pytest` au départ (collez-la) :
  `5 failed, 8 passed` (les 5 échecs : les tests de prédiction et le test du modèle absent, tous en NotImplementedError)
 - Pourquoi certains tests qui attendent un 422 passent-ils déjà, alors que rien n'est écrit ?
  Le schéma était presque vide et refusait tout champ inconnu, donc toute requête, même correcte, recevait un 422. Les tests « mauvaise valeur → 422 » étaient verts pour la mauvaise raison : le refus ne venait pas de la valeur hors bornes mais du schéma vide. Le test `test_predict_valide_renvoie_200` les démasque, car une livraison valide doit être acceptée.
-
## 2. Mon schéma
- Mes bornes et leur justification physique (une ligne par variable) :

| Variable | Min | Max | Pourquoi |
|---|---|---|---|
| distance_km | 1 | 1000 |un trajet de livraison réel ne dépasse pas ~1000 km |
| poids_kg |1 |30000|au-dessus de ~30 t, un camion n’est plus autorisé |
| heure_depart |0| 23|heures d’une journée, entier |
| pluie_mm |0 | 200 |une pluie négative n’existe pas, et 200 mm est déjà extrême |
| trafic_index |0 |10|échelle définie par le contrat : 0 fluide, 10 saturé |
| nb_arrets | 0| 50|un nombre d’arrêts entier, positif, raisonnable pour une tournée |

## 3. Ma fonction predict()
@app.post("/v1/predict", response_model=PredictionOut)
def predict(livraison: Livraison):
    predictor = state.get("predictor")
    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Modèle non chargé : lancez 'python -m logiai.train' puis relancez le serveur.",
        )
    return PredictionOut(**predictor.predict(livraison.model_dump()))

## 4. Quatre requêtes
| Requête | Code obtenu | Pourquoi |
|---|---|---|
| livraison normale | 200|toutes les valeurs respectent le schéma, le modèle est chargé |
| distance_km = -5 |422 | -5 est inférieur à la borne ge=1, refusé par le schéma avant d’appeler predict()|
| type_vehicule = "avion" |422 | pas dans Literal["moto","fourgon","camion"]|
| modèle absent (supprimez models/ et relancez) |503 |state.get("predictor") vaut None, le service est indisponible (côté serveur) |

## 5. Questions de compréhension
1-Chargement au démarrage. Relire model.joblib sur le disque à chaque requête rendrait chaque réponse lente, et avec beaucoup de requêtes simultanées le serveur saturerait le disque et la mémoire. Chargé une seule fois dans lifespan, le modèle reste en mémoire et chaque requête ne fait que le calcul.
2-Qui écrit le contrôle « pluie <= ... » ? C’est le schéma Pydantic, dans logiai/api/schemas.py, avec Field(ge=0, le=200) (adapte au chiffre de ton fichier : ton modèle de CR dit 100, ton schéma dit peut-être 200). FastAPI l’applique tout seul avant d’appeler predict(), donc la route ne voit jamais de valeur impossible.
3-422 vs 503. 422 = erreur du client (4xx) : sa requête est invalide, il doit la corriger. 503 = erreur du serveur (5xx) : la requête est correcte, mais le service n’est pas prêt (modèle absent).
4-/v1/predict plutôt que /predict. /v1 est la version de l’API : le contrat peut évoluer (/v2) sans casser les clients qui utilisent encore /v1.
5-Distance déclarée int. L’API refuserait (422) les distances avec décimales comme 120.5, alors que ce sont des valeurs réelles légitimes. Il faut float pour les grandeurs continues.

## 6. Décision : modèle absent
**Choix : A** (démarrer et répondre 503).
Ce que ça fait perdre : le service a l'air démarré alors qu'il est inutilisable ; un superviseur qui vérifie seulement que le processus tourne croira que tout va bien.
Pourquoi je l'accepte : `/health` reste joignable et indique `model_loaded: false`, donc le superviseur peut détecter et diagnostiquer le problème au lieu de voir une simple « connexion refusée ». Les clients reçoivent un 503 avec un message qui dit quoi faire.
Pourquoi pas B : refuser de démarrer supprime `/health`, donc on ne sait plus pourquoi le service est absent, et un redémarrage automatique pourrait tourner en boucle.

## 7. Lien de la pull request
https://github.com/khadijafl/Atelier3/pulls