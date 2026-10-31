import time
from threading import Timer
import duckdb
from .sql_guard import validate_sql

def execute(df, sql):
    safe = validate_sql(sql)
    start = time.perf_counter()
    con = duckdb.connect(':memory:')
    timer = Timer(10, con.interrupt)
    try:
        con.register('dataset', df)
        con.execute('SET enable_external_access=false')
        con.execute("SET memory_limit='512MB'")
        con.execute('SET threads=2')
        timer.start()
        result = con.execute(f'SELECT * FROM ({safe}) AS result LIMIT 100').df()
        return result, round(time.perf_counter() - start, 4)
    finally:
        timer.cancel()
        timer.join() if timer.ident else None
        con.close()

DEMO_QUERIES = {
    'Vue du portefeuille': ('SELECT COUNT(*) AS lignes, SUM(ClaimNb) AS sinistres, SUM(Exposure) AS exposition, SUM(ClaimNb)/NULLIF(SUM(Exposure),0) AS frequence FROM dataset', {'ClaimNb', 'Exposure'}),
    'Fréquence par région': ('SELECT Region, COUNT(*) AS lignes, SUM(ClaimNb) AS sinistres, SUM(Exposure) AS exposition, SUM(ClaimNb)/NULLIF(SUM(Exposure),0) AS frequence FROM dataset GROUP BY Region ORDER BY frequence DESC LIMIT 100', {'Region', 'ClaimNb', 'Exposure'}),
    'Qualité des expositions': ('SELECT COUNT(*) AS lignes, COUNT(*) FILTER (WHERE Exposure IS NULL OR Exposure <= 0) AS expositions_invalides FROM dataset', {'Exposure'}),
}
