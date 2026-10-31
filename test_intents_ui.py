from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent/'.packages'))
import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

suite=unittest.defaultTestLoader.discover('tests')
if not unittest.TextTestRunner(verbosity=1).run(suite).wasSuccessful(): raise SystemExit(1)
with patch.dict('os.environ',{'OPENAI_API_KEY':'fake-no-network'}):
    app=AppTest.from_file('app.py',default_timeout=90).run()
    assert not app.exception,str(app.exception)
    def send(intent,text,message):
        with patch('services.ai_engine.answer_question',return_value={'intent':intent,'explanation':message,'sql':None,'result':None}) as model:
            app.chat_input[0].set_value(text).run()
            assert not app.exception,str(app.exception)
            assert len(app.code)==0
            return model.call_args
    send('conversation','Merci','Avec plaisir !')
    assert 'pending_question' not in app.session_state
    send('explanation','Can you help me understand the dataset?','Une ligne représente une police automobile observée.')
    assert 'pending_question' not in app.session_state
    send('unavailable','Quel est le coût total ?','Les montants sont absents.')
    assert 'pending_question' not in app.session_state
    send('clarification','Quel taux ?','Quel taux souhaitez-vous calculer ?')
    assert app.session_state['pending_question']=='Quel taux ?'
    call=send('conversation','Merci','Avec plaisir !')
    assert call.args[1]=='Merci'
    assert call.kwargs['business_context']['pending_question']=='Quel taux ?'
    assert app.session_state['pending_question']=='Quel taux ?'
    send('unavailable','Le taux de rentabilité','Les primes et coûts sont absents.')
    assert 'pending_question' not in app.session_state
print('PASS: conversation/explanation/unavailable have no SQL; only clarification creates pending state; thanks remains the current message.')
