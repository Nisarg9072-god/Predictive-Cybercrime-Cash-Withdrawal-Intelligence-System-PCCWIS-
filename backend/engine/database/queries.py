# ---------------------------------------------------------
# SQL Queries for Cybercrime Database
# ---------------------------------------------------------

# Transactions
GET_TRANSACTION_BY_ID = "SELECT * FROM transactions WHERE txn_id = ?"
GET_TRANSACTION_CHAIN = "SELECT * FROM transactions WHERE chain_id = ? ORDER BY hop_layer ASC LIMIT ?"
GET_TERMINAL_CASHOUTS = "SELECT * FROM transactions WHERE is_terminal_cashout = 1 LIMIT ? OFFSET ?"
SEARCH_LAUNDERING_TXNS = "SELECT * FROM transactions WHERE is_laundering = 1 LIMIT ? OFFSET ?"
GET_TXNS_BY_ACCOUNT = "SELECT * FROM transactions WHERE from_account_id = ? OR to_account_id = ? LIMIT ? OFFSET ?"
GET_TXNS_BY_CRIME = "SELECT * FROM transactions WHERE crime_category = ? LIMIT ? OFFSET ?"

# Transaction Aggregations
GET_CHAIN_SUMMARY = """
SELECT chain_id, pattern_type, SUM(amount_inr) as total_amount, MAX(hop_layer) as hop_count 
FROM transactions WHERE chain_id = ? GROUP BY chain_id, pattern_type
"""

# Profiles
GET_PROFILE = "SELECT * FROM profiles WHERE profile_id = ? OR account_id = ?"
SEARCH_PROFILES_BY_NAME = "SELECT * FROM profiles WHERE holder_name LIKE ? LIMIT ? OFFSET ?"
GET_HIGH_RISK_PROFILES = "SELECT * FROM profiles WHERE risk_score >= ? LIMIT ? OFFSET ?"
GET_MULE_PROFILES = "SELECT * FROM profiles WHERE is_mule = 1 LIMIT ? OFFSET ?"
GET_PROFILES_BY_MULE_TYPE = "SELECT * FROM profiles WHERE mule_type = ? LIMIT ? OFFSET ?"
GET_PROFILES_BY_STATE = "SELECT * FROM profiles WHERE last_known_state = ? LIMIT ? OFFSET ?"

# ATMs
GET_ATM_BY_ID = "SELECT * FROM atms WHERE atm_id = ?"
GET_ATMS_BY_STATE = "SELECT * FROM atms WHERE state = ? LIMIT ? OFFSET ?"
GET_ATMS_BY_BANK = "SELECT * FROM atms WHERE bank_code = ? LIMIT ? OFFSET ?"
GET_NEARBY_ATMS = """
SELECT * FROM atms 
WHERE latitude BETWEEN ? AND ? 
  AND longitude BETWEEN ? AND ? 
LIMIT ? OFFSET ?
"""

# Geographic & Stats
GET_DISTRICT = "SELECT * FROM districts WHERE district_name = ? AND state_name = ?"
GET_DISTRICTS_BY_STATE = "SELECT * FROM districts WHERE state_name = ? LIMIT ? OFFSET ?"
GET_STATE_STATS = "SELECT * FROM state_stats WHERE state_name = ?"
GET_HIGH_RISK_STATES = "SELECT * FROM state_stats WHERE risk_tier = 'CRITICAL' OR risk_tier = 'HIGH' ORDER BY amount_reported_cr DESC LIMIT ?"

# Scenarios
# NOTE: data_json column was previously corrupted, but has been fixed.
GET_SCENARIO_SAFE = """
    SELECT scenario_id, scenario_name, crime_category, description,
           victim_city, victim_state, amount_lost_inr, status, data_json
    FROM scenarios WHERE scenario_id = ?
"""
GET_SCENARIO = GET_SCENARIO_SAFE  # backward-compat alias
LIST_SCENARIOS = "SELECT scenario_id, scenario_name, crime_category, status, victim_city, victim_state, amount_lost_inr FROM scenarios LIMIT ? OFFSET ?"
# Search transactions where account_id matches (for victim account discovery)
SEARCH_TXNS_BY_ACCOUNT_PATTERN = """
    SELECT txn_id, chain_id, pattern_type, timestamp_ist, from_account_id,
           from_bank, to_account_id, to_bank, amount_inr, channel,
           is_laundering, hop_layer, is_terminal_cashout, crime_category
    FROM transactions
    WHERE from_account_id LIKE ? OR to_account_id LIKE ?
    LIMIT ? OFFSET ?
"""

# Operational Queries
INSERT_SESSION = "INSERT INTO agent_sessions (session_id, started_at, target_type, target_id, status, created_at) VALUES (?, ?, ?, ?, ?, ?)"
UPDATE_SESSION = "UPDATE agent_sessions SET completed_at = ?, status = ?, iteration_count = ?, tool_call_count = ?, error = ? WHERE session_id = ?"

INSERT_INVESTIGATION = "INSERT INTO investigations (investigation_id, session_id, subject_type, subject_id, objective, status, started_at) VALUES (?, ?, ?, ?, ?, ?, ?)"
UPDATE_INVESTIGATION = "UPDATE investigations SET completed_at = ?, status = ? WHERE investigation_id = ?"

INSERT_OBSERVATION = "INSERT INTO observations (observation_id, investigation_id, source, observation_type, summary, confidence, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)"

INSERT_HYPOTHESIS = "INSERT INTO hypotheses (hypothesis_id, investigation_id, description, category, confidence, status, supporting_observations, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
UPDATE_HYPOTHESIS = "UPDATE hypotheses SET confidence = ?, status = ?, supporting_observations = ?, updated_at = ? WHERE hypothesis_id = ?"

INSERT_DECISION = "INSERT INTO agent_decisions (decision_id, investigation_id, iteration, observation_summary, selected_tool, reason_summary, result_summary, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

INSERT_FINDING = "INSERT INTO findings (finding_id, investigation_id, title, category, severity, confidence, description, evidence_summary, remediation, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

INSERT_AUDIT_EVENT = "INSERT INTO audit_events (event_id, session_id, event_type, component, status, metadata, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)"

INSERT_RISK_ASSESSMENT = "INSERT INTO risk_assessments (risk_assessment_id, investigation_id, iteration, risk_score, risk_level, confidence, indicator_ids, evidence_ids, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"

# Evidence
INSERT_EVIDENCE = """
    INSERT OR IGNORE INTO evidence_items
    (evidence_id, investigation_id, source_type, source_id, observed_field,
     observed_value, description, confidence, timestamp, hash, classification,
     indicator_name, parent_evidence_id, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""
GET_EVIDENCE_BY_INVESTIGATION = """
    SELECT * FROM evidence_items WHERE investigation_id = ? ORDER BY timestamp
"""
GET_EVIDENCE_BY_HASH = "SELECT evidence_id FROM evidence_items WHERE hash = ?"

# Reports
INSERT_REPORT = """
    INSERT OR IGNORE INTO reports
    (report_id, investigation_id, scenario_id, mode, pdf_path, sha256, generated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
"""
GET_REPORT_BY_ID = "SELECT * FROM reports WHERE report_id = ?"
LIST_REPORTS_BY_INVESTIGATION = "SELECT * FROM reports WHERE investigation_id = ? ORDER BY generated_at DESC"

# Finding Lifecycle
INSERT_FINDING_TRANSITION = """
    INSERT INTO finding_transitions
    (transition_id, finding_id, investigation_id, from_status, to_status,
     reason, transitioned_at, transitioned_by)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
"""
GET_FINDING_TRANSITIONS = "SELECT * FROM finding_transitions WHERE finding_id = ? ORDER BY transitioned_at"
GET_FINDINGS_BY_INVESTIGATION = "SELECT * FROM findings WHERE investigation_id = ? ORDER BY created_at"

