"""Small, auditable lexical retrieval corpus; no row embeddings required."""
import re
import unicodedata

DOCUMENTS = [
    {'id': 'MET-006', 'title': 'Âge des véhicules et géographie', 'requires': ['VehAge', 'Region', 'Area'], 'text': 'Âge age véhicules vehicule voiture vehicle : VehAge, en années dans freMTPL2freq. Une moyenne se calcule par AVG(VehAge). Region contient les régions, dont Pays de la Loire ; Area est une classe de zone, pas le nom de région. Filtrer sur Region pour les régions. Calculer la moyenne sur toutes les lignes correspondantes, jamais sur les 100 premières.'},
    {'id': 'MET-001', 'title': 'Fréquence des sinistres', 'requires': ['ClaimNb', 'Exposure'], 'text': 'Fréquence sinistres claims frequency : SUM(ClaimNb) / NULLIF(SUM(Exposure), 0). Exposure représente des années de couverture. Ne pas utiliser la moyenne de ClaimNb ni la moyenne des ratios individuels. Afficher aussi exposition et nombre de contrats.'},
    {'id': 'MET-002', 'title': 'Volume et exposition', 'requires': ['ClaimNb', 'Exposure'], 'text': 'Volume total sinistres : SUM(ClaimNb). Nombre de lignes : COUNT(*). Exposition totale : SUM(Exposure), en années de couverture. Un volume élevé ne suffit pas à conclure à un risque élevé.'},
    {'id': 'MET-003', 'title': 'Segmentation régionale', 'requires': ['Region', 'Exposure'], 'text': 'Région region : segmenter par Region. Comparer fréquence, exposition et effectifs. Les petits groupes sont instables. Une association statistique ne prouve pas une causalité.'},
    {'id': 'MET-004', 'title': 'Coût et rentabilité', 'requires': [], 'text': 'Coût moyen sévérité severity nécessite des montants de sinistres. Rentabilité loss ratio nécessite aussi les primes acquises. Sans ces colonnes, refuser de calculer. Ne jamais inventer montants ou primes.'},
    {'id': 'MET-005', 'title': 'Portée de la démonstration', 'requires': [], 'text': 'Le fichier de démonstration est un échantillon français freMTPL2freq. Il ne représente ni les assurés Foyer ni le marché luxembourgeois. Pas de décision de souscription ou de tarification automatisée.'},
]

def tokens(text):
    text = unicodedata.normalize('NFKD', text.lower())
    words = set(re.findall(r'[a-z0-9]+', ''.join(c for c in text if not unicodedata.combining(c))))
    return words - set('le la les de des du un une et ou en dans pour par est sont quelle quel quelles quels au aux a l d il elle ce ces sur the of in is what for and'.split())

def retrieve(question, columns, limit=3):
    query = tokens(question)
    eligible = [d for d in DOCUMENTS if set(d['requires']) <= set(columns)]
    ranked = sorted(eligible, key=lambda d: len(query & tokens(d['title'] + ' ' + d['text'])), reverse=True)
    return [d for d in ranked if query & tokens(d['title'] + ' ' + d['text'])][:limit]
