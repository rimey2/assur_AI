import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch
import pandas as pd
from services.ai_engine import answer_question


class IntentTests(unittest.TestCase):
    def invoke(self,payload,question):
        fake=SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload)))])
        df=pd.DataFrame({'VehAge':[2,4]})
        with patch('services.ai_engine.OpenAI') as client, patch('services.ai_engine.execute') as executor:
            client.return_value.chat.completions.create.return_value=fake
            executor.return_value=(pd.DataFrame({'moyenne':[3.0]}),0.01)
            answer=answer_question(df,question,'fake')
            return answer,executor.call_count

    def test_non_analytical_never_executes_even_with_sql(self):
        for intent,question in [('conversation','Merci'),('explanation','Présente ce dataset'),('clarification','Quel taux ?'),('unavailable','Quel coût total ?')]:
            with self.subTest(intent=intent):
                answer,calls=self.invoke({'intent':intent,'message':'Texte','sql':'SELECT COUNT(*) FROM dataset'},question)
                self.assertEqual(calls,0)
                self.assertIsNone(answer['sql'])
                self.assertIsNone(answer['result'])

    def test_analysis_executes(self):
        answer,calls=self.invoke({'intent':'analysis','message':'Moyenne des âges','sql':'SELECT AVG(VehAge) AS moyenne FROM dataset'},'Quel âge moyen ?')
        self.assertEqual(calls,1)
        self.assertEqual(answer['result'].iloc[0,0],3.0)

    def test_invalid_contract_fails_closed(self):
        for payload in [{'message':'Texte','sql':'SELECT COUNT(*) FROM dataset'},
                        {'intent':'other','message':'Texte','sql':None},
                        {'intent':'analysis','message':'Texte','sql':None},
                        {'intent':'analysis','message':'Texte','sql':''},
                        {'intent':'conversation','message':None,'sql':None},[]]:
            with self.subTest(payload=payload),self.assertRaises(ValueError):
                self.invoke(payload,'Test')
