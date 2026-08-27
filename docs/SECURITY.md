# Security & Configuration Hardening

## 1. Read-Only Master Database
The master dataset (`cyber_intercept.db`) is accessed strictly using SQLite's read-only URI mode (`?mode=ro`). This prevents any possibility of accidental modification, deletion, or tampering of the forensic source data, even if the agent hallucinates an update query.

## 2. SQL Injection Prevention
All database queries are executed using parameterized SQL (e.g., `cur.execute("SELECT * FROM table WHERE id = ?", (id,))`). The system explicitly does NOT expose a raw SQL execution tool to the agent.

## 3. Sensitive Data Sanitization
A `Sanitizer` middleware runs on all returned data to redact PII (e.g., masking phone numbers, emails, and account identifiers). This ensures that reports and agent internal state do not leak unnecessary personal information.

## 4. Data Provenance
The evidence tracking system strictly requires a `parent_evidence_id` for any information classified as `DERIVED`, `INFERRED`, or `PREDICTED`. The `EvidenceValidator` enforces that inferred evidence cannot be misrepresented as directly `OBSERVED` ground truth.

## 5. False Positive Safeguards
The `RiskEngine` relies entirely on deterministic mapping and scoring. The LLM is NEVER used as an authority for numerical risk scoring or final confidence thresholds. If contradictory evidence is detected, the finding explicitly triggers a safeguard that limits its severity.

## 6. Execution Bounding
Agent loops are bounded by strict configurations (`MAX_ITERATIONS` and `MAX_TOOL_CALLS`) to prevent infinite recursion, uncontrolled resource exhaustion, or unchecked token consumption.
