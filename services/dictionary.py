"""User-reviewed business metadata, bound to one dataset."""
import hashlib
import json
import pandas as pd

DEMO = {
 'IDpol': ('Identifiant de police', 'identifiant'),
 'ClaimNb': ('Nombre de sinistres observés', 'sinistres'),
 'Exposure': ('Durée de couverture observée', 'années'),
 'VehPower': ('Classe de puissance du véhicule', 'classe'),
 'VehAge': ('Âge du véhicule', 'années'),
 'DrivAge': ('Âge du conducteur', 'années'),
 'BonusMalus': ('Coefficient bonus-malus', 'indice'),
 'VehBrand': ('Code de marque du véhicule', 'catégorie'),
 'VehGas': ('Type de carburant', 'catégorie'),
 'Area': ('Classe de zone géographique, distincte de la région', 'classe'),
 'Density': ('Densité de population', 'habitants/km²'),
 'Region': ('Région française', 'catégorie'),
}

def propose(df, demo=False):
    hints={'claim_count':'Nombre de sinistres (proposition à confirmer)',
           'duration':'Durée (préciser ce qui est mesuré)',
           'amount':'Montant (préciser : prime, indemnisation, paiement…)',
           'montant':'Montant (préciser : prime, indemnisation, paiement…)',
           'policy_id':'Identifiant de contrat (proposition à confirmer)',
           'date':'Date (préciser : souscription, survenance, règlement…)'}
    records=[]
    for name in df.columns:
        known=DEMO.get(name) if demo else None
        records.append({'Colonne':name, 'Type':str(df[name].dtype),
            'Définition':known[0] if known else hints.get(name.lower(),''),
            'Unité':known[1] if known else '', 'Validée':bool(known)})
    return pd.DataFrame(records)

def validate(df, records, grain):
    if not isinstance(grain,str) or not grain.strip():
        raise ValueError('Précisez ce que représente une ligne.')
    if [r.get('Colonne') for r in records] != list(df.columns):
        raise ValueError('Le dictionnaire doit correspondre exactement aux colonnes du fichier.')
    pending=[]
    for row in records:
        if not row.get('Validée') or any(not isinstance(row.get(k),str) or not row[k].strip() for k in ('Définition','Unité')):
            pending.append(row['Colonne'])
    if pending:
        raise ValueError('Complétez définition, unité et validation : '+', '.join(pending))
    return {'grain':grain.strip(), 'columns':[{'name':r['Colonne'], 'definition':r['Définition'].strip(), 'unit':r['Unité'].strip()} for r in records]}

def fingerprint(context):
    return hashlib.sha256(json.dumps(context,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
