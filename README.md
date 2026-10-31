# AssurAI — RAG métier et SQL sur un portefeuille assurance



## Interface

- Fichier unique préchargé ; aucune option d'import.
- Questions libres et suggestions, toutes transmises au LLM.
- Tableau de résultats, export CSV et « Voir le SQL généré par le LLM ».
- Contexte métier interne prêt à l'emploi ; aucun dictionnaire à remplir.
- « Nouvelle conversation » réinitialise les échanges et les précisions.



##  Chatbot basé sur une approche RAG ( Fichier, Excel, Duckdb)

- RAG effectué sur le fichier excel. L'utilisateur pose une question
- Le LLM recoit la question et la transforme en requete SQL
- La requete SQL est générée dans Duckdb
- Le LLM renvoie une sur l'interface