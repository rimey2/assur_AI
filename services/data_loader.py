import io
import pandas as pd

MAX_BYTES = 35 * 1024 * 1024
MAX_ROWS = 500_000


def load_dataset(source, filename):
    if isinstance(source, io.BytesIO) and source.getbuffer().nbytes > MAX_BYTES:
        raise ValueError('Fichier supérieur à 35 Mo.')
    if hasattr(source, 'getvalue'):
        raw = source.getvalue()
        if len(raw) > MAX_BYTES:
            raise ValueError('Fichier supérieur à 35 Mo.')
        source = io.BytesIO(raw)
    elif hasattr(source, 'stat') and source.stat().st_size > MAX_BYTES:
        raise ValueError('Fichier supérieur à 35 Mo.')
    if filename.lower().endswith('.xlsx'):
        df = pd.read_excel(source, engine='openpyxl', nrows=MAX_ROWS + 1)
    elif filename.lower().endswith('.csv'):
        try:
            df = pd.read_csv(source, sep=None, engine='python', nrows=MAX_ROWS + 1)
        except UnicodeDecodeError:
            source.seek(0) if hasattr(source, 'seek') else None
            df = pd.read_csv(source, encoding='latin-1', sep=None, engine='python', nrows=MAX_ROWS + 1)
    else:
        raise ValueError('Formats autorisés : .xlsx et .csv')
    if df.empty or len(df.columns) == 0 or len(df) > MAX_ROWS:
        raise ValueError('Le fichier doit contenir entre 1 et 500 000 lignes.')
    df.columns = [str(c).strip() for c in df.columns]
    if any(not c for c in df.columns) or df.columns.duplicated().any():
        raise ValueError('Les noms de colonnes doivent être non vides et uniques.')
    return df


def describe(df):
    return [{'name': c, 'dtype': str(df[c].dtype), 'missing': int(df[c].isna().sum())} for c in df.columns]
