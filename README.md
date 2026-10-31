# AssurAI — RAG métier et SQL sur un portefeuille assurance

Application Streamlit dédiée exclusivement à `data/donnees_assurance.xlsx` (100 000 lignes). Le recruteur pose une question ; le LLM génère du SQL guidé par le schéma, les définitions métier et les libellés retrouvés. DuckDB calcule sur tout le fichier. Le résultat et la requête exécutée sont consultables dans la conversation.

## Lancer sur cette machine

```powershell
cd "C:\Users\aboky\Documents\foyer_group_recrut"
powershell -ExecutionPolicy Bypass -File ".\Lancer_AssurAI.ps1"
```

Ouvrir http://127.0.0.1:8501. La clé reste dans `.streamlit/secrets.toml` (exclu de Git) ou `OPENAI_API_KEY`. Le lanceur local utilise le Python fourni avec Codex et les dépendances `.packages`. Sur une autre machine : installer Python et `requirements.txt`, puis `python -m streamlit run app.py`.

## Interface

- Fichier unique préchargé ; aucune option d'import.
- Questions libres et suggestions, toutes transmises au LLM.
- Tableau de résultats, export CSV et « Voir le SQL généré par le LLM ».
- Contexte métier interne prêt à l'emploi ; aucun dictionnaire à remplir.
- « Nouvelle conversation » réinitialise les échanges et les précisions.

## Limites

Les données sont françaises et ne représentent ni Foyer ni le marché luxembourgeois. Les questions nécessitant primes, montants de sinistres ou dates ne sont pas calculables. SQL en lecture seule sur une table, sans jointure, CTE ni sous-requête. Maximum 100 lignes de sortie ; calculs sur toutes les lignes concernées. L'explication décrit la méthode avant calcul et ne constitue pas une interprétation vérifiée du résultat. Le SQL affiché est celui généré puis normalisé et validé avant exécution. Les réponses du modèle peuvent être erronées et doivent être contrôlées.

Le fournisseur reçoit les questions, le schéma, les définitions et les libellés pertinents ; pas le fichier complet. Prototype local, sans authentification ni quotas applicatifs pour un déploiement public.

## Vérification

`test_single_ui.py` : chargement, absence d'import, contexte du fichier, SQL visible et conservé, nouvelle conversation. Modèle simulé, sans consommation API. Les tests unitaires du dossier `tests` couvrent le moteur SQL et ses protections.


## Routage des intentions

Chaque appel LLM renvoie intent, message et sql. Seule l'intention analysis peut exécuter une requête, après validation SQL. Les intentions conversation, explanation, clarification et unavailable produisent du texte sans tableau ni SQL. Une demande de précision est créée uniquement pour clarification ; les remerciements n'en créent pas et ne déclenchent pas de calcul. Les réponses sans intention valide sont rejetées. Une classification erronée par le modèle reste possible et doit être évaluée avec des questions réelles.

`test_intents_ui.py` vérifie les gardes du moteur et les parcours conversationnels avec un modèle simulé, sans consommation API.
