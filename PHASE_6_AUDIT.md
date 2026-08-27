# Phase 6 Project Audit

## 1. Current Architecture
The system employs a multi-agent orchestrated workflow using LangGraph. The agent interacts with tools connected to a 12GB read-only SQLite master database (`CYBER_INTERCEPT_FULL_DATASET`) while maintaining an operational memory layer in a separate SQLite database. The reporting layer generates cryptographic-hashed PDF reports.

## 2. Existing Components
- **Agent (`agent/`)**: Manages `InvestigationState`, graph nodes (observe, hypothesize, plan, execute, evaluate), and tool registration.
- **Database (`database/`)**: Handles connections to read-only and operational DBs, queries, repositories, and sanitization.
- **Risk (`risk/`)**: Deterministic risk engine mapping evidence to findings, indicators, and confidence scores.
- **Evidence (`evidence/`)**: Collects, deduplicates, and formats structured evidence items.
- **Remediation (`remediation/`)**: Deterministic mappings from findings to remediation recommendations.
- **Reporting (`reporting/`)**: Orchestrates finding generation, explainability, PDF output, and SHA-256 validation.

## 3. Existing CLI Commands
- `python -m cli.main db health`
- `python -m cli.main db schema`
- `python -m cli.main investigate scenario <ID>`
- `python -m cli.main report investigation <ID> [--synthetic-demo]`
- `python -m cli.main report verify <REPORT_ID>`

## 4. Database Architecture
- **Master Dataset (`cyber_intercept.db`)**: 12GB read-only database (currently featuring known corruption in `idx_atms_geo`).
- **Operational Database (`agent.db`)**: Writable state database tracking agent sessions, investigations, observations, hypotheses, decisions, evidence, findings, and audit events.

## 5. Agent Loop
The loop consists of sequential state-driven nodes:
1. `observe_node`: Synthesizes current context.
2. `hypothesis_node`: Proposes investigation directions.
3. `planner_node`: Selects tools based on hypothesis and current evidence.
4. `tool_execution_node`: Runs selected tools.
5. `evaluate_node`: Assesses tool output, generates findings via `RiskEngine`, and scores risk.

## 6. Risk Engine
Calculates risk scores (0-100) deterministically from aggregated evidence items and triggered indicators. Outputs confidence and maps to standard severities (LOW, MODERATE, HIGH, CRITICAL).

## 7. Evidence Pipeline
Structured `EvidenceItem` model classifying data into OBSERVED, DERIVED, INFERRED, PREDICTED, or SYNTHETIC. Enforces integrity via `EvidenceValidator` and removes duplicates using `EvidenceDeduplicator` based on cryptographic hashes.

## 8. Reporting Pipeline
`ReportBuilder` constructs a `SecurityAssessmentReport`. `PDFGenerator` (using ReportLab Platypus) outputs a formatted PDF with 18 structured sections. `ReportHasher` produces a SHA-256 signature for integrity. Includes strict REAL vs SYNTHETIC separation.

## 9. Test Coverage
- Unit tests for all major components (Phase 4, Phase 5).
- Operational DB integration tests (`test_risk_engine.py`, `test_evidence_db.py`).
- Synthetic E2E tests (`test_synthetic_e2e.py`).
- Real-data corruption tests (`test_real_data_blocked.py`).
Currently 97 tests passing, 3 xfailed (due to DB corruption handling).

## 10. Known Limitations
- Master database contains a corrupted B-tree index (`idx_atms_geo`).
- LLM provider is currently mocked/disabled (`LLMProvider(available=False)`).
- The system heavily relies on deterministic rules in place of LLM evaluation due to offline/mock constraints.

## 11. Technical Debt
- Some methods in `RiskEngine` rely on hardcoded mappings.
- The state evaluation logic in `nodes.py` could be cleaner.
- `InvestigationResult` is missing a formal cohesive model.

## 12. Missing Production-Readiness Components
- Comprehensive API layer (`api/`).
- Formal Evaluation Engine (`evaluation/`).
- `InvestigationResult` holistic data model.
- Strong false-positive/negative safeguards (tests for explicit traceability).
- Dedicated synthetic demo command (`demo run`).
- `system status` and `evaluate investigation` CLI commands.
- Production documentation (`docs/`).
