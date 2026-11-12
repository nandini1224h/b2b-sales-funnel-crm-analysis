"""Engineered synthetic CRM project, not independently observed business data."""
from pathlib import Path
import random
import sqlite3
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
SEED=42
SOURCES = {'Cold outbound':52,'Partner referrals':1276,'Organic search':360,
           'Paid search':280,'Webinars':252,'Paid social':200}
REP_WINS=[250,270,290,300,310,320,330,350]
SPEND=[600000,400000,500000,900000,600000,800000]
def generate():
    rng=random.Random(SEED)
    winners=[f'R{i+1:02}' for i,w in enumerate(REP_WINS) for _ in range(w)]
    others=[f'R{i+1:02}' for i,w in enumerate(REP_WINS) for _ in range(3000-w)]
    rng.shuffle(winners); rng.shuffle(others)
    rows=[]
    for source,nwins in SOURCES.items():
        flags=[1]*nwins+[0]*(4000-nwins); rng.shuffle(flags)
        for won in flags:
            rep=(winners if won else others).pop()
            created=pd.Timestamp('2026-01-01')+pd.Timedelta(days=rng.randrange(181))
            # All outcomes observed inside 90 days; every lead has >=92 days follow-up.
            contact=rng.random() < (0.97 if source=='Partner referrals' else 0.78)
            qualify=contact and rng.random() < (0.8 if source=='Partner referrals' else 0.52)
            propose=qualify and rng.random()<0.65
            if won: contact=qualify=propose=True
            stages=[created]
            for reached in [contact,qualify,propose]:
                stages.append(stages[-1]+pd.Timedelta(days=rng.randint(1,12)) if reached else pd.NaT)
            depth=3 if propose else 2 if qualify else 1 if contact else 0
            end=stages[depth]+pd.Timedelta(days=rng.randint(1,30))
            open_lead=not won and rng.random()<0.12
            status='Won' if won else ('Open' if open_lead else 'Lost')
            first_hours=rng.choice([1,2,4,8,12,24,48,72]) if contact else None
            value=rng.randrange(30,151)*1000
            rows.append(dict(lead_id=f'L{len(rows)+1:06}',account_id=f'A{len(rows)+1:06}',
                source=source,rep_id=rep,region=rng.choice(['North','South','East','West']),
                industry=rng.choice(['Manufacturing','Retail','IT services','Logistics']),
                company_size=rng.choice(['1-50','51-200','201-1000']),created_at=created,
                contacted_at=stages[1],qualified_at=stages[2],proposal_at=stages[3],
                closed_at=pd.NaT if open_lead else end,status=status,
                lost_reason=None if status!='Lost' else rng.choice(['No response','Poor fit','Price','Competitor','Timing']),
                first_response_hours=first_hours,deal_value_inr=value,revenue_inr=value if won else 0))
    leads=pd.DataFrame(rows)
    reps=pd.DataFrame([dict(rep_id=f'R{i+1:02}',rep_name=f'Rep {i+1}',tenure_months=12+i*3) for i in range(8)])
    costs=pd.DataFrame([dict(source=s,spend_inr=c) for s,c in zip(SOURCES,SPEND)])
    (ROOT/'data').mkdir(exist_ok=True)
    leads.to_csv(ROOT/'data/leads.csv',index=False,date_format='%Y-%m-%d')
    reps.to_csv(ROOT/'data/reps.csv',index=False); costs.to_csv(ROOT/'data/source_spend.csv',index=False)
    db=sqlite3.connect(ROOT/'data/crm.sqlite')
    db.execute('PRAGMA foreign_keys=ON')
    db.executescript((ROOT/'sql/schema.sql').read_text())
    # Schema is retained; inserts run in a transaction and honor constraints.
    with db:
        db.execute('DELETE FROM leads'); db.execute('DELETE FROM reps'); db.execute('DELETE FROM source_spend')
        reps.to_sql('reps',db,if_exists='append',index=False)
        costs.to_sql('source_spend',db,if_exists='append',index=False)
        leads.to_sql('leads',db,if_exists='append',index=False)
    db.close()
    print(f'Generated {len(leads):,} synthetic leads with seed {SEED}.')
if __name__=='__main__': generate()
