PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS reps (
 rep_id TEXT PRIMARY KEY, rep_name TEXT NOT NULL, tenure_months INTEGER NOT NULL CHECK(tenure_months>=0));
CREATE TABLE IF NOT EXISTS source_spend (
 source TEXT PRIMARY KEY, spend_inr REAL NOT NULL CHECK(spend_inr>=0));
CREATE TABLE IF NOT EXISTS leads (
 lead_id TEXT PRIMARY KEY, account_id TEXT NOT NULL UNIQUE,
 source TEXT NOT NULL REFERENCES source_spend(source), rep_id TEXT NOT NULL REFERENCES reps(rep_id),
 region TEXT NOT NULL, industry TEXT NOT NULL, company_size TEXT NOT NULL,
 created_at TEXT NOT NULL, contacted_at TEXT, qualified_at TEXT, proposal_at TEXT, closed_at TEXT,
 status TEXT NOT NULL CHECK(status IN ('Won','Lost','Open')), lost_reason TEXT,
 first_response_hours REAL, deal_value_inr REAL NOT NULL CHECK(deal_value_inr>=0),
 revenue_inr REAL NOT NULL CHECK(revenue_inr>=0),
 CHECK(status!='Won' OR (closed_at IS NOT NULL AND revenue_inr>0 AND proposal_at IS NOT NULL)),
 CHECK(status!='Open' OR closed_at IS NULL));
CREATE INDEX IF NOT EXISTS idx_leads_source_rep ON leads(source,rep_id);
CREATE INDEX IF NOT EXISTS idx_leads_created ON leads(created_at);
