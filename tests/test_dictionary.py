import unittest
from unittest.mock import patch
from types import SimpleNamespace
import json
import pandas as pd
from services.dictionary import propose,validate,fingerprint
from services.ai_engine import answer_question

class DictionaryTests(unittest.TestCase):
    def setUp(self):
        self.df=pd.DataFrame({'Amount':[10,20], 'Duration':[30,60]})

    def test_unknown_requires_review(self):
        rows=propose(self.df).to_dict('records')
        self.assertFalse(any(r['Validée'] for r in rows))
        with self.assertRaises(ValueError): validate(self.df,rows,'Un paiement')
        for r in rows: r.update({'Définition':'Définition confirmée','Unité':'EUR','Validée':True})
        with self.assertRaises(ValueError): validate(self.df,rows,'')
        context=validate(self.df,rows,'Un paiement')
        changed=dict(context,grain='Un contrat')
        self.assertNotEqual(fingerprint(context),fingerprint(changed))
        with self.assertRaises(ValueError): validate(self.df,rows[::-1],'Un paiement')

    def test_context_is_sent_and_clarification_does_not_execute(self):
        context={'demo':False,'grain':'Un paiement', 'columns':[{'name':'Amount','definition':'Indemnisation','unit':'EUR'}]}
        payload={'intent':'clarification','sql':None,'message':'Quelle durée souhaitez-vous utiliser ?'}
        fake=SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload)))])
        with patch('services.ai_engine.OpenAI') as client, patch('services.ai_engine.execute') as executor:
            client.return_value.chat.completions.create.return_value=fake
            answer=answer_question(self.df,'Quel montant annuel ?','fake',business_context=context)
            self.assertIsNone(answer['sql'])
            executor.assert_not_called()
            messages=client.return_value.chat.completions.create.call_args.kwargs['messages']
            self.assertIn('Indemnisation',messages[1]['content'])
            self.assertIn('EUR',messages[1]['content'])
            self.assertNotIn('MET-00',messages[1]['content'])
