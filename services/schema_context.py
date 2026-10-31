"""Resolve category mentions locally; only matched labels enter the prompt."""
import re
import unicodedata
from .data_loader import describe

def normalize(value):
    value=unicodedata.normalize('NFKD',str(value).casefold())
    return ' '.join(re.findall(r'[a-z0-9]+',''.join(c for c in value if not unicodedata.combining(c))))

def question_schema(df,question):
    schema=describe(df)
    normalized=' '+normalize(question)+' '
    for column in schema:
        series=df[column['name']]
        if str(series.dtype) not in ('object','string','category','str'):
            continue
        matches=[]
        for value in series.dropna().unique():
            label=normalize(value)
            if len(label)>=3 and (' '+label+' ') in normalized:
                matches.append(str(value))
                if len(matches)==10:
                    break
        if matches:
            column['matched_values']=matches
    return schema
