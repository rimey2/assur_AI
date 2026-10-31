from pathlib import Path
import os
import pandas as pd
import streamlit as st
from services.data_loader import load_dataset
from services.dictionary import propose, validate
from services.ai_engine import answer_question

st.set_page_config(page_title='AssurAI — Questions sur le portefeuille',page_icon='◈',layout='wide',initial_sidebar_state='expanded')
st.markdown('''<style>
.block-container{max-width:1120px;padding-top:2.5rem;padding-bottom:3rem}
h1,h2,h3{letter-spacing:-.035em}
[data-testid="stChatMessage"]{border:1px solid #293b50;border-radius:14px;margin-top:12px}
[data-testid="stMetric"]{background:#142235;border:1px solid #293b50;border-radius:12px;padding:16px}
.eyebrow{color:#66dfc5;font-size:.75rem;letter-spacing:.16em;font-weight:700}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#142235 0%,#0d1726 100%);border-right:1px solid #2b4056}
.side-brand{font-size:1.65rem;font-weight:750;letter-spacing:-.04em;color:#edf5fb;margin:8px 0}
.side-tagline{color:#afc0d2;font-size:.88rem;line-height:1.55;margin-bottom:24px}
.side-step{padding:17px 15px;margin:12px 0;border:1px solid #30465d;border-radius:14px;background:#17283b}
.side-number{display:inline-block;color:#79e6ce;background:#183f43;border:1px solid #2b6462;border-radius:8px;padding:3px 8px;font-size:.76rem;font-weight:700;letter-spacing:.06em;margin-bottom:10px}
.side-step h3{font-size:1rem!important;letter-spacing:-.01em;margin:0 0 7px;padding:0;color:#f0f6fc}
.side-step p{font-size:.86rem;line-height:1.55;color:#bdccdc;margin:0}
.side-flow{font-size:.81rem;color:#79e6ce;line-height:1.7;padding:14px 0;border-top:1px solid #30465d;margin-top:22px}
/* Keep the walkthrough visible even when Streamlit remembers a collapsed state. */
[data-testid="stSidebar"]{position:relative!important;transform:none!important;margin-left:0!important;width:310px!important;min-width:310px!important;max-width:310px!important;flex-shrink:0!important;visibility:visible!important;transition:none!important}
[data-testid="stSidebarContent"]{display:block!important;visibility:visible!important}
[data-testid="stSidebarCollapseButton"],[data-testid="collapsedControl"],button[aria-label="Expand sidebar"]{display:none!important}
</style>''',unsafe_allow_html=True)
with st.sidebar:
    st.markdown('''<div class="eyebrow">Architecture · RAG / SQL</div>
<div class="side-brand">◈ AssurAI</div>
<div class="side-tagline">Du prompting au calcul vérifiable.<br>Explorez le MVP en trois étapes.</div>
<div class="side-step"><span class="side-number">01 · QUESTION</span><h3>Posez votre question</h3><p>Interrogez vos données d'assurance : profils des véhicules, sinistres ou comparaisons entre régions.</p></div>
<div class="side-step"><span class="side-number">02 · SQL</span><h3>Inspectez le SQL généré</h3><p>Appuiyez sur le bouton (Voir le SQL généré) sous la réponse. Examinez les colonnes, les filtres et les agrégations utilisés (SQL généré par Open AI).</p></div>
<div class="side-step"><span class="side-number">03 · RÉSULTAT</span><h3>Consultez la réponse</h3><p>Lisez la méthode et le résultat calculé sur le fichier complet. Vérifiez les chiffres et exportez le tableau en CSV.</p></div>
<div class="side-flow">Contexte métier → LLM → SQL validé → DuckDB</div>''',unsafe_allow_html=True)
    with st.expander('Sous le capot · AI Engineering'):
        st.markdown('**Retrieval** — Recherche lexicale de fiches métier et rapprochement des libellés du fichier.\n\n**Génération** — schéma et contexte transmis au LLM pour produire le SQL.\n\n**Exécution** — validation de l’arbre syntaxique SQL, lecture seule et calcul dans DuckDB.\n\n**Traçabilité** — SQL exécuté, durée du calcul et résultats consultables.')
root=Path(__file__).parent
if st.session_state.get('intent_routing_version') != 1:
    st.session_state.pop('pending_question',None)
    st.session_state['intent_routing_version']=1
try:
    secret=st.secrets.get('OPENAI_API_KEY','')
except Exception:
    secret=''
key=(os.environ.get('OPENAI_API_KEY','') or secret).strip()

@st.cache_data(show_spinner='Chargement du portefeuille assurance…')
def load_portfolio(path,marker):
    df=load_dataset(Path(path),Path(path).name)
    context=validate(df,propose(df,demo=True).to_dict('records'),
        'Une ligne représente une observation de police automobile sur sa période d’exposition.')
    context.update(demo=True,notes='Échantillon français freMTPL2freq. Region contient les régions, Area les classes de zone. Aucune prime ni montant de sinistre dans ce fichier. Exposure est en années. Aucune date calendaire disponible.')
    return df,context

path=root/'data/donnees_assurance.xlsx'
try:
    identity=f'{path.stat().st_mtime_ns}:{path.stat().st_size}'
    df,context=load_portfolio(str(path),identity)
except Exception as exc:
    st.error(f'Impossible de charger donnees_assurance.xlsx : {exc}')
    st.stop()

if st.session_state.get('ui_version')!=5 or st.session_state.get('dataset_id')!=identity:
    for name in ('uploaded_df','upload_identity','business_context','context_version','dictionary_rows','dictionary_editor','grain_input','notes_input','pending_question','clarifications'):
        st.session_state.pop(name,None)
    st.session_state.update(ui_version=5,dataset_id=identity,messages=[])

st.markdown('<div class="eyebrow">ASSURAI · ASSISTANT RAG / SQL</div>',unsafe_allow_html=True)
st.title("Interrogez vos données d'Assurance automobiles")
st.write('Posez votre question dans la langue de votre choix. Le modèle génère une requête SQL, puis le calcul est exécuté sur le fichier complet.')
left,right=st.columns(2)
left.metric("Nombre de lignes(nombre d'observation de polices automobiles)",f'{len(df):,}'.replace(',',' '))
right.metric('Variables disponibles',len(df.columns))
st.caption("Source : [Dataset Huggingface](https://huggingface.co/datasets/mabilton/fremtpl2/tree/main)· Données sur les contrats d'assurance automobile.(fichier freMTPL2freq.csv)")

with st.expander('Quelles sont les variables de ma base à interroger?'):
    st.dataframe(pd.DataFrame(context['columns']).rename(columns={'name':'Colonne','definition':'Définition','unit':'Unité'}),hide_index=True,width='stretch')
    st.caption('Le contexte métier et les libellés pertinents guident le modèle.Poser uniquement des questions sur les données du fichier pour des réponses satisfaisantes')
    st.caption('Le fournisseur IA reçoit la question, le schéma, les définitions métier et les libellés retrouvés, pas les 100 000 lignes. Le SQL autorisé est en lecture seule, sur une table, sans jointure ni sous-requête.')
    st.caption('Posez librement les questions sur les données disponibles. Assurez vous néanmoins que les questions aient rapport aux données. Vérifiez toujours le SQL et les résultats avant utilisation.')

if not key:
    with st.expander('Configuration organisateur',expanded=True):
        key=st.text_input('Clé API pour cette session',type='password')
        st.caption('Ou ajoutez la clé dans .streamlit/secrets.toml puis redémarrez AssurAI.')
    if not key:
        st.info('Configurez la clé API pour activer les questions et la génération de SQL.')

suggestions=['Quel est l’âge moyen des véhicules dans les Pays de la Loire ?',
             'Quelle est la fréquence des sinistres par région ?',
             'Combien de contrats ont au moins un sinistre ?']
selected=None
if not st.session_state['messages']:
    st.caption('EXEMPLES DE QUESTIONS')
    for column,suggestion in zip(st.columns(3),suggestions):
        if column.button(suggestion,width='stretch',disabled=not bool(key)):
            selected=suggestion
if st.button('Nouvelle conversation'):
    st.session_state['messages']=[]
    st.session_state.pop('pending_question',None)
    st.session_state['clarifications']=[]
    st.rerun()

def render_answer(answer,index):
    st.write(answer['explanation'])
    if answer.get('intent') in ('conversation','explanation','clarification','unavailable'):
        return
    result=answer.get('result')
    if result is not None:
        if result.empty:
            st.warning('Aucune ligne ne correspond aux filtres. Vérifiez les conditions dans le SQL.')
        else:
            st.dataframe(result,hide_index=True,width='stretch')
            if result.shape==(1,1) and pd.isna(result.iloc[0,0]):
                st.info('Le calcul ne produit pas de valeur : données absentes ou dénominateur nul.')
            st.download_button('Exporter le résultat CSV',result.to_csv(index=False).encode('utf-8-sig'),file_name='resultat_assurai.csv',mime='text/csv',key=f'csv_{index}')
    if answer.get('sql'):
        with st.expander('Voir le SQL généré'):
            st.code(answer['sql'],language='sql')
            st.caption(f"SQL validé et exécuté sur l'ensemble des données · {answer.get('elapsed',0):.3f} s de calcul · 100 lignes de résultat maximum.")
            for source in answer.get('sources',[]):
                st.caption(f"Contexte métier : {source['id']} — {source['title']}")

for index,message in enumerate(st.session_state['messages']):
    with st.chat_message(message['role']):
        if message['role']=='user':
            st.write(message['text'])
        else:
            render_answer(message['answer'],index)
if st.session_state.get('pending_question'):
    st.info('Répondez à la demande de précision, ou choisissez « Nouvelle conversation » pour changer de sujet.')
question=st.chat_input('Posez votre question sur le portefeuille…',disabled=not bool(key)) or selected
if question:
    st.session_state['messages'].append({'role':'user','text':question})
    with st.chat_message('user'):
        st.write(question)
    pending=st.session_state.get('pending_question')
    effective=question
    call_context=dict(context)
    call_context['clarifications']=st.session_state.get('clarifications',[])[-8:]
    if pending:
        call_context['pending_question']=pending
        call_context['clarifications']+=[{'question':pending,'precision':question}]
    with st.chat_message('assistant'):
        try:
            with st.spinner('Compréhension de votre demande…'):
                answer=answer_question(df,effective,key,business_context=call_context)
            render_answer(answer,len(st.session_state['messages']))
            st.session_state['messages'].append({'role':'assistant','answer':answer})
            if answer.get('intent') == 'analysis':
                if pending:
                    st.session_state['clarifications']=call_context['clarifications'][-8:]
                st.session_state.pop('pending_question',None)
            elif answer.get('intent') == 'clarification':
                st.session_state['pending_question']=(f'{pending}\nPrécision : {question}' if pending else question)
            elif answer.get('intent') in ('explanation', 'unavailable'):
                st.session_state.pop('pending_question',None)
        except Exception as exc:
            st.error('La réponse n’a pas pu être calculée. Reformulez ou vérifiez la configuration API.')
            st.caption(f'Diagnostic : {type(exc).__name__}')
st.caption('Posez librement les questions sur les données disponibles. Assurez vous néanmoins que les questions aient rapport aux données. Vérifiez toujours le SQL et les résultats avant utilisation.')

