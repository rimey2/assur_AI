"""Conservative SQL policy for demo: one SELECT over the registered dataset."""
import sqlglot
from sqlglot import exp

ALLOWED_FUNCTIONS = {
    'COUNT','SUM','AVG','MIN','MAX','ROUND','ABS','COALESCE','NULLIF',
    'LOWER','UPPER','TRIM','LENGTH','CAST','TRY_CAST','DATE_TRUNC',
    'YEAR','MONTH','DAY','EXTRACT','FLOOR','CEIL','CEILING','STDDEV',
    'MEDIAN','QUANTILE_CONT','COUNT_IF','IF','GREATEST','LEAST',
}
FORBIDDEN = (exp.Command, exp.Insert, exp.Update, exp.Delete, exp.Create,
             exp.Drop, exp.Alter, exp.Copy, exp.Attach, exp.Pragma,
             exp.Set, exp.Merge, exp.Transaction)


def validate_sql(sql):
    statements = sqlglot.parse(sql.strip().rstrip(';'), read='duckdb')
    if len(statements) != 1 or not isinstance(statements[0], exp.Select):
        raise ValueError('Seule une requête SELECT simple est autorisée.')
    tree = statements[0]
    if tree.find(exp.Join) or tree.find(exp.Into):
        raise ValueError('Jointures et SELECT INTO interdits.')
    if tree.find(exp.With) or tree.find(exp.Union) or tree.find(exp.Subquery):
        raise ValueError('CTE, UNION et sous-requêtes non autorisés dans ce MVP.')
    if any(tree.find(t) for t in FORBIDDEN):
        raise ValueError('Instruction SQL interdite.')
    tables = list(tree.find_all(exp.Table))
    if len(tables) != 1 or tables[0].name.lower() != 'dataset' or tables[0].db or tables[0].catalog:
        raise ValueError('La requête doit lire uniquement la table dataset.')
    for f in tree.find_all(exp.Func):
        if f.sql_name().upper() not in ALLOWED_FUNCTIONS:
            raise ValueError(f'Fonction SQL non autorisée : {f.sql_name()}')
    return tree.sql(dialect='duckdb')
