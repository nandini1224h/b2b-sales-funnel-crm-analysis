# Interview and resume guide

## A clear 60–90 second explanation

“I built a reproducible B2B sales analytics project using SQL, SQLite and Python. It uses 24,000 synthetic leads across six acquisition sources, eight reps and four regions. I engineered the dataset to test the calculations in my original project brief, so I disclose that the headline percentages are simulated rather than independent company findings.

“I defined conversion as a lead becoming won within 90 days and used mature lead-created cohorts to avoid unequal follow-up. SQL produced source, rep, region and funnel tables; Python reconciled the results, added Wilson intervals and generated an offline visual report.

“The simulated source gap is 1.3% versus 31.9%, or 24.54 times. Raw rep conversion ranges from 8.33% to 11.67%, which is a 40% relative gap. I also standardized reps to the same source mix; that reduces the gap to around 35.6%. My recommendation is a capped budget experiment and qualification review, with volume and margin guardrails. I did not claim a real budget move or realized uplift.”

Use this as an explanation after you have actually opened, run and studied the project. Do not describe yourself as having implemented or understood work you have not reviewed.

## How each original resume claim maps to evidence

| Original language | Project evidence | Accurate interpretation |
|---|---|---|
| Diagnosed a critical pain point | Source and stage reports | Located simulated leakage for investigation; did not establish a real cause |
| 24× conversion-rate gap | 1,276/4,000 divided by 52/4,000 | 24.54×, usually written 24.5× |
| Segmented by source, rep and region | `source_rep_region.csv`, grouped SQL | 192 combinations; examine counts before comparing |
| Using SQL and Python | SQL queries, pandas reconciliation, plotting | Both execute in the rebuild |
| 40% rep performance gap | 11.67% vs. 8.33% raw conversion | Relative conversion difference, not broad “performance” |
| Driving budget recommendations to stakeholders | Fictional stakeholder memo | Proposed recommendations; no real stakeholder delivery or decision |

## Recommended resume version

**B2B Sales Funnel & CRM Analysis | SQL, Python, SQLite**

- Built a reproducible SQL/Python pipeline for 24,000 synthetic CRM leads, segmenting funnel and acquisition-cost performance by source, rep and region.
- Evaluated a designed 24.5× source conversion gap and 40% raw relative rep gap, added source-adjusted comparisons, and developed a controlled budget-reallocation proposal.

If you want the strongest honest wording without emphasizing engineered results:

- Built a SQL/Python analytics project on 24,000 simulated B2B leads, with mature-cohort conversion metrics, funnel diagnostics and acquisition-cost reporting.
- Standardized rep comparisons for source mix and translated results into a stakeholder memo with an incremental-budget experiment and business guardrails.

Avoid “increased conversions,” “saved budget,” “drove stakeholder decisions” or “delivered revenue growth” unless you later do and measure those things in a real setting.

## Questions you should be able to answer

### 1. Where did the data come from?

A seeded generator included in the repository. The exact source and rep headline metrics were engineered to reproduce a project brief. This is not production CRM or a public benchmark dataset.

### 2. Why use 90-day conversion?

A consistent observation window makes cohorts comparable. If older leads have six months and newer leads only two weeks to win, a source concentrated in recent months can look unfairly weak. Eligible leads must be at least 90 days old, and wins must occur within those 90 days.

### 3. What is the denominator?

All unique mature created leads, including open and lost ones. Wins divided by closed opportunities answers a different question: close rate among resolved opportunities.

### 4. Why is it 24.54× rather than 24%?

The calculation divides two rates: 31.9/1.3. It is a ratio. The absolute difference is 30.6 percentage points. The relative percentage increase is approximately 2,354%.

### 5. What does a 40% rep gap mean?

The highest rate, 350/3,000, is 1.4 times the lowest rate, 250/3,000. Subtract one and multiply by 100 to get 40%. The absolute difference is 3.33 percentage points.

### 6. How did you avoid blaming reps for lead mix?

I calculated win rates within source for each rep and weighted them by a common portfolio source distribution. The adjusted gap is smaller. I would still need quality, territory, tenure, workload and assignment controls to make stronger claims.

### 7. Could Simpson's paradox occur?

Yes. A rep can rank worse overall because they handle more difficult sources despite performing better within comparable sources. This dataset demonstrates source adjustment, but it does not necessarily demonstrate an actual ranking reversal. Do not claim it does.

### 8. Why not move every rupee to referrals?

Historical conversion does not measure marginal response to spend. Referrals may be capacity-limited, the additional leads may be less qualified, and outbound may generate strategic accounts. Use an incremental pilot with capacity and margin checks.

### 9. What does your CAC mean?

It is acquisition spend divided by won leads. It excludes salary and overhead, so I call it a channel acquisition-cost proxy. Fully loaded customer acquisition cost needs a broader, consistently timed cost basis and unique new customers.

### 10. Did the analysis prove the cause of outbound leakage?

No. It identified a simulated low-conversion segment and a weak transition. Diagnosing root cause requires notes, calls, account fit and preferably experiments. The generator itself forces winners through all stages, so causal interpretations would be especially inappropriate.

### 11. Why Wilson intervals?

They quantify binomial proportion uncertainty more robustly near small rates than a naive symmetric interval. In this engineered simulation, they illustrate the technique rather than validate a population claim. Independence and representative sampling would also matter with real data.

### 12. What was the hardest analytical issue?

Defining comparable metrics and separating descriptive differences from causal recommendations. Source attribution, cohort maturity and cost aggregation can each produce apparently impressive but misleading results if handled badly.

### 13. What can go wrong when joining spend?

If one INR 600,000 source-spend row joins to 4,000 raw lead rows, summing that amount counts the budget 4,000 times. Aggregate lead metrics to source first, then join the single source-spend row.

### 14. How do you handle missing CRM values?

In this dataset, stage nulls intentionally mean the stage was not reached; dimensions are complete. With real data, distinguish unknown status from not reached, audit missingness by source, deduplicate lead/account records, validate timestamps and quarantine invalid rows. The existing project does not pretend to have performed those real-world cleanup steps.

### 15. Why SQLite instead of a cloud warehouse?

Portability and reproducibility. The database fits in one file, SQL is inspectable, and a reviewer needs no account. For scale I would use an appropriate warehouse, incremental ingestion and scheduled transformations; none is needed for 24,000 rows.

### 16. How do you know the output is correct?

Five tests verify grain/integrity, date maturity and chronology, independent SQL/pandas agreement and headline arithmetic, funnel nesting and full rep-source coverage. Database constraints add another layer. A passing suite verifies implementation invariants, not business realism.

### 17. What would you improve next?

Use an independently sourced dataset; make snapshot/cohort dates configurable; implement one reusable cohort view for every query; add real account and assignment history; measure margins; and validate incremental budget effects with a properly designed experiment.

### 18. How would this work on a live CRM?

Export or ingest only permitted fields, retain source IDs, normalize timestamps and currencies, model accounts and opportunities separately, define attribution, maintain a snapshot history and run quality checks. Schedule analysis only after those definitions are agreed. No live integration is implemented here.

## Hands-on preparation

1. Extract the package and open the dashboard.
2. Explain the two headline calculations without reading notes.
3. Run `python run.py` and the test command.
4. Read the first SQL query line by line: cohort, flag, aggregation, cost join.
5. Query one source/rep/region cell and reconcile it with the CSV.
6. Calculate cold outbound proposal-to-win by hand.
7. Describe why adjusted rep rates differ from raw rates.
8. Read the memo and explain the difference between a recommendation and implemented impact.
9. Change one chart title or add a useful SQL query so you can discuss a concrete modification you made.
10. Replace the synthetic data with independently sourced records if you want evidence of real findings.

## A sensible six-minute demonstration

- First minute: business problem and synthetic-data disclosure.
- Second minute: cohort, schema and conversion definition.
- Third minute: source chart and funnel leakage.
- Fourth minute: raw versus adjusted rep comparison.
- Fifth minute: cost limitations and capped experiment.
- Sixth minute: SQL implementation, validation and next steps.
