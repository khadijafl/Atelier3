# Compte rendu : TP API LogiAI

**Nom:** Flija  **Groupe :** 4

## 1. Environnement et premiers tests
- Sortie de `python -m pytest` au départ (collez-la) :
- Pourquoi certains tests qui attendent un 422 passent-ils déjà, alors que rien n'est écrit ?

## 2. Mon schéma
- Mes bornes et leur justification physique (une ligne par variable) :

| Variable | Min | Max | Pourquoi |
|---|---|---|---|
| distance_km | 1 | 1000 | |
| poids_kg | | | |
| heure_depart | | | |
| pluie_mm | | | |
| trafic_index | | | |
| nb_arrets | | | |

## 3. Ma fonction predict()
(collez le code)

## 4. Quatre requêtes
| Requête | Code obtenu | Pourquoi |
|---|---|---|
| livraison normale | 200| |
| distance_km = -5 |422 | |
| type_vehicule = "avion" |422 | |
| modèle absent (supprimez models/ et relancez) |503 | |

## 5. Questions de compréhension
1. Pourquoi charge-t-on le modèle au démarrage et pas à chaque requête ?
2. Qui écrit le contrôle « pluie <= 100 », et où est-il écrit ?
3. Différence entre 422 et 503 ?
4. Pourquoi une route `/v1/predict` plutôt que `/predict` ?
5. Que se passerait-il si la distance était déclarée `int` ?

## 6. Décision : modèle absent
Répondre 503 ou refuser de démarrer ? Qu'est-ce que chaque option fait perdre ?

## 7. Lien de la pull request
