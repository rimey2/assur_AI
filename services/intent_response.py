"""Validate model output before deciding whether any SQL may execute."""
INTENTS = {'conversation', 'explanation', 'analysis', 'clarification', 'unavailable'}


def parse_response(payload):
    if not isinstance(payload, dict):
        raise ValueError('La réponse du modèle doit être un objet JSON.')
    intent = payload.get('intent')
    if not isinstance(intent, str) or intent not in INTENTS:
        raise ValueError('Intention manquante ou non reconnue dans la réponse du modèle.')
    message = payload.get('message')
    if not isinstance(message, str) or not message.strip():
        raise ValueError('Message manquant dans la réponse du modèle.')
    sql = None
    if intent == 'analysis':
        value = payload.get('sql')
        if not isinstance(value, str) or not value.strip():
            raise ValueError('Une analyse doit fournir une requête SQL non vide.')
        sql = value.strip()
    # Even if the model erroneously supplies SQL for another intent, discard it.
    return {'intent': intent, 'explanation': message.strip(), 'sql': sql, 'result': None}
