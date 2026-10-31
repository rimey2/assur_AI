import unittest
import pandas as pd
from services.query_engine import execute
from services.sql_guard import validate_sql
from services.knowledge import retrieve

class CoreTests(unittest.TestCase):
    def test_weighted_frequency(self):
        df = pd.DataFrame({'ClaimNb': [1, 1], 'Exposure': [0.1, 1.]})
        result, _ = execute(df, 'SELECT SUM(ClaimNb)/NULLIF(SUM(Exposure),0) AS f FROM dataset')
        self.assertAlmostEqual(result.iloc[0,0], 2/1.1)

    def test_reject_unsafe(self):
        for sql in ['DROP TABLE dataset', "SELECT * FROM read_csv_auto('x.csv')", 'SELECT * FROM dataset; SELECT * FROM dataset', 'SELECT * FROM dataset JOIN dataset b ON TRUE', 'SELECT * FROM other', 'SELECT * FROM (SELECT * FROM dataset)', "COPY dataset TO 'x.csv'"]:
            with self.subTest(sql=sql), self.assertRaises(Exception):
                validate_sql(sql)

    def test_cap_and_zero(self):
        df = pd.DataFrame({'x': range(150), 'Exposure': [0]*150})
        result, _ = execute(df, 'SELECT x FROM dataset')
        self.assertEqual(len(result), 100)
        result, _ = execute(df, 'SELECT SUM(x)/NULLIF(SUM(Exposure),0) AS f FROM dataset')
        self.assertTrue(pd.isna(result.iloc[0,0]))

    def test_retrieval_and_schema_scope(self):
        self.assertEqual(retrieve('fréquence sinistres', ['ClaimNb','Exposure'])[0]['id'], 'MET-001')
        self.assertNotIn('MET-001', [d['id'] for d in retrieve('fréquence sinistres', ['ventes'])])

if __name__ == '__main__':
    unittest.main()
