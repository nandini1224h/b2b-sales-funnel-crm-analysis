-- SQLite dialect. Fixed snapshot, lead-created cohort, won within 90 days.
-- Run: python src/analyze.py. Each named query is exported to outputs/.
-- name: source_performance
WITH cohort AS (
 SELECT *,CASE WHEN status='Won' AND julianday(closed_at)-julianday(created_at)<=90 THEN 1 ELSE 0 END AS won90
 FROM leads WHERE created_at>='2026-01-01' AND created_at<'2026-07-01'
 AND julianday('2026-09-30')-julianday(created_at)>=90
), metrics AS (
 SELECT source,COUNT(*) AS leads,SUM(won90) AS wins,
 100.0*SUM(won90)/COUNT(*) AS conversion_pct,
 SUM(CASE WHEN won90=1 THEN revenue_inr ELSE 0 END) AS revenue_inr
 FROM cohort GROUP BY source
)
SELECT m.*,s.spend_inr,1.0*s.spend_inr/m.leads AS cost_per_lead_inr,
 1.0*s.spend_inr/NULLIF(m.wins,0) AS acquisition_cost_proxy_inr,
 1.0*m.revenue_inr/NULLIF(s.spend_inr,0) AS revenue_to_spend
FROM metrics m JOIN source_spend s USING(source) ORDER BY conversion_pct DESC;

-- name: rep_performance
SELECT l.rep_id,r.rep_name,COUNT(*) AS leads,SUM(l.status='Won') AS wins,
100.0*SUM(l.status='Won')/COUNT(*) AS conversion_pct
FROM leads l JOIN reps r USING(rep_id) GROUP BY l.rep_id,r.rep_name ORDER BY conversion_pct DESC;

-- name: source_rep_region
SELECT source,rep_id,region,COUNT(*) AS leads,SUM(status='Won') AS wins,
100.0*SUM(status='Won')/COUNT(*) AS conversion_pct
FROM leads GROUP BY source,rep_id,region ORDER BY source,rep_id,region;

-- name: region_performance
SELECT region,COUNT(*) AS leads,SUM(status='Won') AS wins,
100.0*SUM(status='Won')/COUNT(*) AS conversion_pct
FROM leads GROUP BY region ORDER BY conversion_pct DESC;

-- name: funnel_by_source
SELECT source,COUNT(*) AS leads,COUNT(contacted_at) AS contacted,
COUNT(qualified_at) AS qualified,COUNT(proposal_at) AS proposed,SUM(status='Won') AS won
FROM leads GROUP BY source ORDER BY source;

-- name: monthly_cohort
SELECT substr(created_at,1,7) AS cohort_month,COUNT(*) AS leads,SUM(status='Won') AS wins,
100.0*SUM(status='Won')/COUNT(*) AS conversion_pct
FROM leads GROUP BY cohort_month ORDER BY cohort_month;

-- name: lost_reasons
SELECT source,lost_reason,COUNT(*) AS lost_leads
FROM leads WHERE status='Lost' GROUP BY source,lost_reason ORDER BY source,lost_leads DESC;

-- name: response_time
SELECT CASE WHEN first_response_hours<=4 THEN '01: <=4h'
WHEN first_response_hours<=24 THEN '02: 5-24h'
WHEN first_response_hours IS NOT NULL THEN '03: >24h' ELSE '04: Uncontacted' END AS response_bucket,
COUNT(*) AS leads,SUM(status='Won') AS wins,100.0*SUM(status='Won')/COUNT(*) AS conversion_pct
FROM leads GROUP BY response_bucket ORDER BY response_bucket;

-- name: cycle_time
SELECT source,COUNT(*) AS wins,AVG(julianday(closed_at)-julianday(created_at)) AS mean_days_to_win
FROM leads WHERE status='Won' GROUP BY source;

-- name: source_adjusted_rep
-- Direct standardization: each rep gets the portfolio's source weights.
WITH cells AS (
 SELECT rep_id,source,COUNT(*) AS n,1.0*SUM(status='Won')/COUNT(*) AS rate
 FROM leads GROUP BY rep_id,source
), weights AS (
 SELECT source,1.0*COUNT(*)/(SELECT COUNT(*) FROM leads) AS weight FROM leads GROUP BY source
)
SELECT rep_id,100*SUM(rate*weight) AS source_adjusted_conversion_pct,MIN(n) AS smallest_source_cell
FROM cells JOIN weights USING(source) GROUP BY rep_id ORDER BY source_adjusted_conversion_pct DESC;
