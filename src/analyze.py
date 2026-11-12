"""Reproducible descriptive analysis. No causal or production-impact claims."""
from pathlib import Path
import sqlite3,re,json,math,html
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs'
def wilson(w,n):
    z=1.96;p=w/n;d=1+z*z/n
    center=(p+z*z/(2*n))/d; half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return 100*(center-half),100*(center+half)
def analyze():
    OUT.mkdir(exist_ok=True)
    db=sqlite3.connect(ROOT/'data/crm.sqlite')
    result={}
    for name,query in re.findall(r'-- name: (\w+)\n(.*?)(?=-- name: |\Z)',(ROOT/'sql/analysis.sql').read_text(),re.S):
        result[name]=pd.read_sql_query(query,db)
    leads=pd.read_sql_query('SELECT * FROM leads',db); db.close()
    src=result['source_performance']; rep=result['rep_performance']
    src[['ci_low_pct','ci_high_pct']]=[wilson(w,n) for w,n in zip(src.wins,src.leads)]
    for k,v in result.items(): v.to_csv(OUT/f'{k}.csv',index=False)
    gap=src.iloc[0].conversion_pct/src.iloc[-1].conversion_pct
    rep_gap=(rep.iloc[0].conversion_pct/rep.iloc[-1].conversion_pct-1)*100
    metrics=dict(leads=len(leads),wins=int((leads.status=='Won').sum()),conversion_pct=100*(leads.status=='Won').mean(),source_ratio=float(gap),rep_relative_gap_pct=float(rep_gap),rep_percentage_point_gap=float(rep.iloc[0].conversion_pct-rep.iloc[-1].conversion_pct),synthetic=True)
    (OUT/'metrics.json').write_text(json.dumps(metrics,indent=2))
    plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(10,5)); order=src.sort_values('conversion_pct')
    ax.barh(order.source,order.conversion_pct,color=['#7b8aa0']*5+['#14b8a6'])
    ax.errorbar(order.conversion_pct,range(len(order)),xerr=[order.conversion_pct-order.ci_low_pct,order.ci_high_pct-order.conversion_pct],fmt='none',ecolor='#16243b',capsize=3)
    ax.set(xlabel='90-day lead-to-win conversion (%)',title='Partner referrals lead; source mix matters')
    for i,r in enumerate(order.itertuples()): ax.text(r.conversion_pct+1.5,i,f'{r.conversion_pct:.1f}% · {r.wins:,}/{r.leads:,}',va='center',fontsize=9)
    ax.set_xlim(0,45);fig.tight_layout();fig.savefig(OUT/'source_conversion.png',dpi=170);plt.close(fig)
    adj=result['source_adjusted_rep']; combined=rep.merge(adj,on='rep_id').sort_values('rep_id')
    fig,ax=plt.subplots(figsize=(10,5));x=list(range(len(combined)))
    ax.bar([i-.18 for i in x],combined.conversion_pct,.36,label='Raw',color='#334e78')
    ax.bar([i+.18 for i in x],combined.source_adjusted_conversion_pct,.36,label='Source adjusted',color='#14b8a6')
    ax.set_xticks(x,combined.rep_id);ax.set(ylabel='Lead-to-win conversion (%)',title='Rep gap: descriptive, not proof of rep skill');ax.legend();fig.tight_layout();fig.savefig(OUT/'rep_conversion.png',dpi=170);plt.close(fig)
    funnel=result['funnel_by_source'][['leads','contacted','qualified','proposed','won']].sum()
    fig,ax=plt.subplots(figsize=(10,5));ax.bar(funnel.index,funnel.values,color='#334e78')
    for i,n in enumerate(funnel): ax.text(i,n+250,f'{n:,}',ha='center')
    ax.set(ylabel='Leads reaching stage',title='Cumulative sales funnel · synthetic cohort');fig.tight_layout();fig.savefig(OUT/'sales_funnel.png',dpi=170);plt.close(fig)
    sections=''.join(f'<section><h2>{html.escape(k.replace("_"," ").title())}</h2>{v.round(3).to_html(index=False,border=0)}</section>' for k,v in result.items())
    report=f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>B2B CRM analysis</title><style>body{{margin:0;background:#eef2f7;color:#16243b;font:16px system-ui}}main{{max-width:1180px;margin:auto;padding:36px 24px}}header{{background:#16243b;color:white;padding:32px;border-radius:16px}}.cards{{display:flex;gap:16px;flex-wrap:wrap;margin:24px 0}}.card,section{{background:white;padding:22px;border-radius:12px;margin-bottom:22px;overflow:auto}}.card{{flex:1;min-width:170px}}strong{{font-size:30px}}table{{border-collapse:collapse;white-space:nowrap;width:100%;font-size:13px}}td,th{{padding:10px;text-align:left;border-bottom:1px solid #e1e7ef}}img{{max-width:100%;height:auto}}p{{line-height:1.65}}@media print{{body{{background:white}}header{{color:black;background:white}}}}</style><main><header><p>PORTFOLIO PROJECT · SIMULATED DATA</p><h1>B2B sales funnel & CRM analysis</h1><p>January–June 2026 lead cohorts · Snapshot 30 September 2026 · 90-day conversion window</p></header><div class="cards"><div class="card"><strong>{len(leads):,}</strong><p>Unique leads</p></div><div class="card"><strong>{metrics['wins']:,}</strong><p>Won within 90 days</p></div><div class="card"><strong>{metrics['conversion_pct']:.2f}%</strong><p>Overall conversion</p></div><div class="card"><strong>{gap:.2f}×</strong><p>Highest / lowest source rate</p></div></div><section><h2>Decision brief</h2><p>Partner referrals convert at 31.9% (1,276/4,000); cold outbound at 1.3% (52/4,000). The ratio is 24.54×, and the absolute gap is 30.6 percentage points. These values were deliberately engineered in a simulated dataset.</p><p>Highest rep conversion is 11.67%; lowest is 8.33%. The relative gap is 40%, or 3.33 percentage points. Rep comparisons need source, territory, tenure and account-quality controls before performance action.</p><p>Recommend a limited reallocation experiment, with qualified lead volume, contribution margin, capacity and marginal acquisition cost guardrails. No budget was actually moved and no realized uplift is claimed.</p></section><section><img src="source_conversion.png" alt="Source conversion rates and Wilson intervals"><img src="rep_conversion.png" alt="Raw and source adjusted rep conversion"><img src="sales_funnel.png" alt="Cumulative funnel stage counts"></section>{sections}<section><h2>Limits</h2><p>One lead per account; no repeat deals. Outcomes, response times, spend and deal sizes are simulated. Intervals illustrate sampling methods, not uncertainty about real business performance. Response-time associations are affected by construction and selection. Source adjustment does not control every confounder. Spend excludes salaries and is an acquisition-cost proxy, not fully loaded CAC. Revenue is booked won value, not collected cash or profit.</p></section></main></html>"""
    (OUT/'dashboard.html').write_text(report,encoding='utf-8')
    print(json.dumps(metrics,indent=2))
if __name__=='__main__': analyze()
