import unittest
from unittest.mock import patch
from types import SimpleNamespace
import json
import pandas as pd
from services.ai_engine import answer_question
from services.knowledge import retrieve
from services.schema_context import question_schema

class VehicleAgeTest(unittest.TestCase):
    def test_actual_labels_and_custom_import(self):
        df=pd.DataFrame({'Region':['Pays-de-la-Loire'], 'Area':['B'], 'Produit':['Épargne-vie']})
        schema=question_schema(df,'âge dans les pays de la loire')
        self.assertEqual(schema[0]['matched_values'],['Pays-de-la-Loire'])
        self.assertNotIn('matched_values',schema[1])
        self.assertEqual(question_schema(df,'total epargne vie')[2]['matched_values'],['Épargne-vie'])
    def test_average_not_first_100(self):
        df = pd.DataFrame({'VehAge': [1]*100 + [101], 'Region': ['Pays de la Loire']*101, 'Area': ['B']*101})
        sql = "SELECT AVG(VehAge) AS age_moyen FROM dataset WHERE Region = 'Pays de la Loire'"
        fake = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps({'intent':'analysis','sql':sql,'message':'Moyenne sur la région.'})))])
        with patch('services.ai_engine.OpenAI') as client:
            client.return_value.chat.completions.create.return_value = fake
            answer = answer_question(df, 'Quelle est la moyenne âge des véhicules dans les pays de la loire ?', 'fake')
            self.assertAlmostEqual(answer['result'].iloc[0,0],201/101)
            messages = client.return_value.chat.completions.create.call_args.kwargs['messages']
            self.assertIn('AVG', messages[0]['content'])
            self.assertIn('MET-006', messages[1]['content'])

    def test_relevant_context(self):
        docs=retrieve('Quelle est la moyenne âge des véhicules dans les pays de la loire ?', ['VehAge','Region','Area'])
        self.assertEqual(docs[0]['id'],'MET-006')
        self.assertNotIn('MET-005',[d['id'] for d in docs])
