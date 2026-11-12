"""Validate grain, funnel chronology, cohort maturity and independent SQL/Python agreement."""
import unittest,sqlite3,json
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
class AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.leads=pd.read_csv(ROOT/'data/leads.csv')
        cls.db=sqlite3.connect(ROOT/'data/crm.sqlite')
    @classmethod
    def tearDownClass(cls): cls.db.close()
    def test_grain_and_integrity(self):
        d=self.leads
        self.assertEqual(len(d),24000);self.assertTrue(d.lead_id.is_unique);self.assertTrue(d.account_id.is_unique)
        self.assertEqual(self.db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
        self.assertEqual(self.db.execute('PRAGMA foreign_key_check').fetchall(),[])
        self.assertTrue((d.revenue_inr[d.status!='Won']==0).all())
        self.assertTrue(d.closed_at[d.status=='Open'].isna().all())
    def test_chronology_and_maturity(self):
        d=self.leads
        for a,b in [('created_at','contacted_at'),('contacted_at','qualified_at'),('qualified_at','proposal_at')]:
            rows=d[d[b].notna()]
            self.assertTrue(rows[a].notna().all())
            self.assertTrue((pd.to_datetime(rows[b])>=pd.to_datetime(rows[a])).all())
        closed=d[d.closed_at.notna()]
        self.assertTrue(((pd.to_datetime(closed.closed_at)-pd.to_datetime(closed.created_at)).dt.days<=90).all())
        for col in ['created_at','contacted_at','qualified_at','proposal_at']:
            rows=closed[closed[col].notna()]
            self.assertTrue((pd.to_datetime(rows.closed_at)>=pd.to_datetime(rows[col])).all())
        self.assertTrue(((pd.Timestamp('2026-09-30')-pd.to_datetime(d.created_at)).dt.days>=90).all())
        self.assertTrue(d.proposal_at[d.status=='Won'].notna().all())
    def test_sql_python_agreement(self):
        source=pd.read_csv(ROOT/'outputs/source_performance.csv').set_index('source')
        py=self.leads.assign(won=self.leads.status=='Won').groupby('source').won.agg(['count','sum','mean'])
        for s in py.index:
            self.assertEqual(source.loc[s,'wins'],py.loc[s,'sum'])
            self.assertEqual(source.loc[s,'leads'],py.loc[s,'count'])
            self.assertAlmostEqual(source.loc[s,'conversion_pct'],100*py.loc[s,'mean'])
        self.assertAlmostEqual(source.loc['Partner referrals','conversion_pct'],31.9)
        self.assertAlmostEqual(source.loc['Cold outbound','conversion_pct'],1.3)
        self.assertAlmostEqual(31.9/1.3,24.53846153846)
        r=self.leads.assign(won=self.leads.status=='Won').groupby('rep_id').won.mean()
        self.assertAlmostEqual((r.max()/r.min()-1)*100,40)
    def test_funnel_is_nested(self):
        f=pd.read_csv(ROOT/'outputs/funnel_by_source.csv')
        for a,b in zip(['leads','contacted','qualified','proposed'],['contacted','qualified','proposed','won']):
            self.assertTrue((f[a]>=f[b]).all())
    def test_nonempty_adjustment_cells(self):
        d=self.leads.groupby(['rep_id','source']).size()
        self.assertEqual(len(d),48);self.assertGreater(d.min(),0)
if __name__=='__main__': unittest.main()
