from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent/'.packages'))
from unittest.mock import patch
import pandas as pd
from streamlit.testing.v1 import AppTest

with patch.dict('os.environ',{'OPENAI_API_KEY':'test-only-no-network'}):
    app=AppTest.from_file('app.py',default_timeout=90).run()
    assert not app.exception,str(app.exception)
    assert app.metric[0].value=='100 000'
    assert len(app.radio)==0
    assert not app.get('file_uploader')
    assert not app.get('data_editor')
    answer={'intent':'analysis','sql':'SELECT COUNT(*) AS lignes FROM dataset','explanation':'Nombre de lignes du portefeuille.', 'result':pd.DataFrame({'lignes':[100000]}),'elapsed':0.01}
    with patch('services.ai_engine.answer_question',return_value=answer) as engine:
        app.chat_input[0].set_value('Combien de lignes contient le fichier ?').run()
        assert engine.call_args.kwargs['business_context']['demo'] is True
        assert len(engine.call_args.args[0])==100000
    assert not app.exception,str(app.exception)
    assert any('COUNT(*)' in code.value for code in app.code)
    app.run()
    assert any('COUNT(*)' in code.value for code in app.code)
    next(b for b in app.button if b.label=='Nouvelle conversation').click().run()
    assert len(app.session_state['messages'])==0
    assert not app.exception,str(app.exception)
print('PASS: fixed workbook, no upload/editor, LLM question with portfolio context, visible SQL, persistent result, reset.')
