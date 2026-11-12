# Detailed project guide

## 1. The story you are implementing

A fictional B2B software business receives leads through cold outbound, partner referrals, organic search, paid search, webinars and paid social. Marketing celebrates lead volume; sales complains about weak qualification. Management asks whether the problem is lead quality, the sales process or representative performance.

Your analyst role is to define a reliable denominator, produce an auditable dataset, segment conversion, diagnose where the funnel thins, and recommend a test. The deliverable is a decision-support analysis, not a predictive model or a live CRM application.

The core business tension is that equal lead counts do not imply equal revenue opportunity. A referral often arrives with trust and intent; an outbound lead may have little intent. Even a large descriptive conversion difference cannot tell you what happens if the business spends another rupee on referrals.

## 2. Analytical contract

**Grain:** one unique lead representing one unique company/account. Every lead belongs to exactly one source, representative and region. One account can contribute at most one win in this model.

**Population:** leads created on or after 1 January 2026 and before 1 July 2026.

**Observation date:** 30 September 2026. Every eligible lead must be at least 90 days old.

**Numerator:** eligible leads whose deal is won within 90 days of creation.

**Denominator:** all eligible created leads, including open, lost and won leads. Excluding open leads would inflate the rate and change the business question.

**Conversion formula:** `100 × won_within_90_days / mature_created_leads`.

**Attribution:** one assigned source per lead, interpreted as CRM acquisition source. This is single-touch attribution. The data does not record multiple marketing touches, so multi-touch attribution is out of scope.

**Money:** INR. Revenue is the booked value of a won deal. It is not recognized accounting revenue, collected cash, recurring revenue or profit.

**Cost:** source acquisition spend for these cohorts. Sales salary, overhead, retention cost and referral commissions outside the supplied spend are excluded. Call the result a channel acquisition-cost proxy rather than fully loaded CAC.

## 3. Data dictionary

### leads.csv / leads table

| Field | Meaning | Rule |
|---|---|---|
| lead_id | Synthetic lead identifier | Unique and non-null |
| account_id | Synthetic company identifier | Unique in this model |
| source | Acquisition channel | One of six source dimension rows |
| rep_id | Assigned sales representative | Foreign key to reps |
| region | North, South, East or West | Simulated territory |
| industry | Manufacturing, Retail, IT services, Logistics | Simulated company category |
| company_size | 1–50, 51–200, 201–1000 | Simulated employee band |
| created_at | Cohort entry date | January–June 2026 |
| contacted_at | First contacted stage date | Null if not reached |
| qualified_at | Qualification date | Requires contact |
| proposal_at | Proposal date | Requires qualification |
| closed_at | Won/lost closure date | Null for open leads |
| status | Won, Lost or Open | Terminal result as of snapshot |
| lost_reason | Recorded reason for lost lead | Null for non-lost leads |
| first_response_hours | Simulated contact response measure | Null for uncontacted |
| deal_value_inr | Potential deal size | Nonnegative |
| revenue_inr | Won booked value | Zero for non-won |

### Other tables

`reps` contains `rep_id`, anonymous `rep_name` and `tenure_months`. Tenure is available as a context variable but not used as a causal control.

`source_spend` contains one row per source with `spend_inr`. Always aggregate leads to source first, then join spend. Joining source spend to raw leads and summing it would multiply the cost by the lead count.

## 4. How the generator works—and why that matters

The seed is 42. Each source contributes exactly 4,000 leads. Win totals are predetermined: cold outbound 52, referrals 1,276, organic 360, paid search 280, webinars 252 and paid social 200. That yields 2,420 wins overall.

Eight representatives each receive exactly 3,000 leads. Their predetermined wins are 250, 270, 290, 300, 310, 320, 330 and 350. The generator shuffles winner and non-winner representative pools, then assigns them to the source rows. This satisfies both the source totals and rep totals while allowing source mix to vary slightly by representative.

Contact, qualification and proposal stages are generated probabilistically for non-winners. Every winner is required to reach all three stages. Dates are chronological; the maximum simulated closure lag is 66 days. Some non-winning leads remain open at the snapshot. Industry, size and region are random categories.

This is an engineered demonstration. Do not say you discovered these exact metrics in an independent dataset. Also do not interpret simulated response-time or regional patterns as real behavior. Random region assignment makes small regional variation expected noise, and forced complete stages for winners affects stage and response associations.

To turn this into a stronger future project, acquire a public/licensed CRM dataset, map its schema, freeze a cohort definition and let the actual metrics emerge. Do not tune its rows to reproduce your resume.

## 5. Build and inspect the database

`sql/schema.sql` defines primary keys, foreign keys, status checks and nonnegative amount constraints. The generator loads dimensions before leads and builds source/rep and creation-date indexes.

Open `data/crm.sqlite` in a SQLite client if you want a graphical SQL editor, or query it through Python:

```python
import sqlite3
import pandas as pd
connection = sqlite3.connect('data/crm.sqlite')
print(pd.read_sql_query('SELECT source, COUNT(*) AS leads FROM leads GROUP BY source', connection))
connection.close()
```

SQLite was chosen because anyone can run the project without maintaining a server. Conditional aggregation uses SQLite expressions such as `SUM(status='Won')`. To port to PostgreSQL, replace those with `SUM(CASE WHEN status='Won' THEN 1 ELSE 0 END)` and translate `julianday`/date syntax. The schema is relational, so the analytical structure ports easily even though the SQL is not dialect-neutral.

## 6. Source analysis

The first query creates an eligible cohort, computes a `won90` flag and aggregates by source. It joins source-level spend only after aggregation.

| Source | Leads | Wins | Conversion | Spend INR | Spend / win INR |
|---|---:|---:|---:|---:|---:|
| Partner referrals | 4,000 | 1,276 | 31.9% | 400,000 | 313.48 |
| Organic search | 4,000 | 360 | 9.0% | 500,000 | 1,388.89 |
| Paid search | 4,000 | 280 | 7.0% | 900,000 | 3,214.29 |
| Webinars | 4,000 | 252 | 6.3% | 600,000 | 2,380.95 |
| Paid social | 4,000 | 200 | 5.0% | 800,000 | 4,000.00 |
| Cold outbound | 4,000 | 52 | 1.3% | 600,000 | 11,538.46 |

The source contrast has three distinct mathematical descriptions:

- Rate ratio: `31.9 / 1.3 = 24.5385`, about 24.5×.
- Absolute difference: `31.9 - 1.3 = 30.6 percentage points`.
- Relative increase: `(31.9 - 1.3) / 1.3 × 100 = 2,353.85%`.

Do not interchange them. A 24.5× ratio is not a 24.5% improvement.

The report adds Wilson 95% intervals. For cold outbound the interval is roughly 0.99%–1.70%; for referrals it is roughly 30.47%–33.36%. Wilson intervals work better than a naive symmetric normal interval near small proportions. In an engineered dataset, they demonstrate statistical computation, not evidence about a real-world business population.

## 7. Funnel diagnosis

The cumulative funnel is Lead → Contacted → Qualified → Proposed → Won. A row remains counted in every stage it reached even after it is lost or won.

Use two types of rates:

- Cumulative rate: stage reached / all leads. Useful for comparing the complete journey.
- Transition rate: stage reached / immediately preceding stage. Useful for diagnosing a specific process boundary.

Cold outbound reaches 3,119 contacts, 1,671 qualifications, 1,129 proposals and 52 wins. Its proposal-to-win rate is `52 / 1,129 = 4.61%`. Referrals reach 3,908 contacts, 3,367 qualifications, 2,633 proposals and 1,276 wins; proposal-to-win is `1,276 / 2,633 = 48.46%`.

The largest absolute source difference among these conditional transitions is at proposal-to-win, about 43.86 percentage points. This identifies a place to investigate. It does not prove that proposals are bad. Low intent, poor qualification, unsuitable accounts, pricing and attribution could all cause this pattern. Stage selection also changes the population being compared.

Do not interpret cumulative stage counts as chronological inventory: they are counts of leads that ever reached each stage, not a snapshot count currently sitting in each stage.

## 8. Representative comparison

Raw conversion ranks R08 highest at 11.67% and R01 lowest at 8.33%.

`(11.6667 / 8.3333 - 1) × 100 = 40%`.

This is a 40% higher conversion rate relative to the low rep. It is a 3.33 percentage-point gap. It is not proof that the strongest rep is 40% more productive in revenue or effort.

A raw ranking can reward favorable lead assignments. The project therefore calculates direct source standardization:

1. Calculate each rep's win rate within each source.
2. Calculate the overall portfolio's source mix.
3. Multiply each rep-source rate by the common source weight.
4. Sum across all six sources for each rep.

Because this simulation has equal source volumes, all weights are 1/6. R08's adjusted conversion is about 11.42% and R01's is about 8.42%; the adjusted relative difference is approximately 35.6%. The exact raw 40% headline therefore becomes smaller after one observable assignment factor is controlled.

Every rep-source cell is populated; the minimum cell count is checked and exported. In real data, absent or tiny cells make standardization unstable. Restrict to common support or use a carefully specified model rather than silently replacing missing rates with zero.

Source adjustment does not remove account-quality, industry, territory, tenure, workload or selection bias. Do not make compensation or personnel decisions from this ranking alone. For source-by-rep-by-region output, inspect cell counts before interpreting differences.

## 9. Region, cohort, loss and response analysis

Regional conversion ranges from about 9.58% in East to 10.51% in West. Since regions were randomly generated, this is a demonstration of segmentation and should not trigger territory reallocations.

Monthly cohorts compare leads by creation month. A fixed mature-cohort window avoids giving January leads six months to convert while giving June leads only one month. The source query implements an explicit 90-day window. Secondary queries rely on the generated dataset's maturity invariants; change those queries before loading a broader live dataset.

Loss reasons are assigned randomly to lost leads. They demonstrate a `GROUP BY` report and investigation workflow, not a validated causal pain point. Real CRM reason fields often require auditing against notes and calls.

Response-time buckets are ≤4 hours, 5–24 hours, >24 hours and uncontacted. A faster-response association, if observed, is not causal. High-intent leads may be contacted sooner, uncontacted leads are structurally unable to win in this generator, and successful leads were forced through contact.

Cycle time uses won leads only and reports mean creation-to-win days. This is subject to survivorship bias. It cannot estimate how long every lead takes to resolve. For real open pipelines, use survival methods or clearly separate age from closed-deal cycle time.

## 10. Cost and scenario interpretation

Cost per lead = source spend / source leads. Acquisition-cost proxy = source spend / source wins. Revenue-to-spend = booked won value / acquisition spend. None of these is contribution margin or fully loaded ROI.

All monetary values were invented and intentionally simple. The unusually high revenue-to-spend ratios are not realistic forecasts. Do not extrapolate them to an actual company.

A useful scenario is shifting INR 100,000 from cold outbound into partner development and organic acquisition, subject to capacity and eligibility checks. If the old outbound averages held, that spend corresponds to about `100,000 / 150 = 667` leads and `667 × 1.3% = 8.67` wins. That is a historical-average opportunity-cost scenario, not a forecast of actual lost deals.

Do not estimate referral upside as `100,000 / 313.48` guaranteed additional wins. Referral channels have finite partners, incentive effects, saturation and variable quality; marginal acquisition economics can be much worse than historical averages. Estimate a range from a pilot instead.

## 11. Validation

The included suite checks:

1. Unique lead/account grain, 24,000 records, SQLite integrity, foreign keys, non-won revenue and open closure rules.
2. Funnel chronology, nested timestamps, 90-day maturity and timely outcomes.
3. Independent pandas aggregation against SQL source results, plus source ratio and rep gap arithmetic.
4. Monotonically decreasing cumulative funnel counts.
5. Complete rep-source comparison cells.

The build produced 24,000 leads and 2,420 wins; all five tests passed. The HTML report and charts are generated from executed query outputs rather than manually typed source result tables.

## 12. Suggested presentation order

Spend roughly five minutes on the project: business question, metric definition, data model, one source chart, the raw/adjusted rep chart, then the recommendation and experiment. Keep the generator disclosure in the first minute. Open the SQL and show the mature-cohort CTE if asked for technical depth.

To build your own understanding, rerun it, change a source's win count while preserving the total rep wins, add a stage transition query, and explain why the output changes. To extend the generator with a different total win count, update the rep win pool too. The current pool totals must equal the source win totals.
