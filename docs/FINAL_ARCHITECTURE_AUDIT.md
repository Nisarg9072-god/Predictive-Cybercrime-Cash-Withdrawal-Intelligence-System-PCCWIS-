# FINAL ARCHITECTURE AUDIT

## Current Architecture

The system is a LangGraph-based multi-agent cybercrime investigation framework built across 6 development phases. The core pipeline is:

```
CLI Input → PredictiveCybercrimeAgent → LangGraph State Machine → Dataset Tools
         → RiskEngine → EvidenceCollector → ReportBuilder → PDFGenerator → SHA-256
```

---

## Files That Are Actually Used (Core Execution Path)

### Agent
| File | Purpose | Status |
|---|---|---|
| `agent/agent.py` | Main orchestrator, initialises LangGraph run | USED |
| `agent/graph/state.py` | InvestigationState TypedDict | USED |
| `agent/graph/nodes.py` | observe/hypothesis/plan/execute/evaluate nodes | USED |
| `agent/graph/edges.py` | Routing logic between nodes | USED |
| `agent/graph/graph.py` | LangGraph graph assembly | USED |
| `agent/llm_provider.py` | LLM stub (currently always returns UNAVAILABLE) | USED BUT STUB |
| `agent/result.py` | InvestigationResult Pydantic model | USED |
| `agent/tools/registry.py` | Tool registry | USED |
| `agent/tools/transaction_tools.py` | DB-backed transaction tools | USED |
| `agent/tools/profile_tools.py` | DB-backed profile tools | USED |
| `agent/tools/atm_tools.py` | DB-backed ATM tools | USED |
| `agent/tools/scenario_tools.py` | DB-backed scenario tools | USED |
| `agent/tools/registry_types.py` | ToolResult Pydantic model | USED |

### Database
| File | Purpose | Status |
|---|---|---|
| `database/connection.py` | Read-only dataset connection + operational connection | USED |
| `database/models.py` | Pydantic models for DB rows | USED |
| `database/queries.py` | All SQL query strings | USED |
| `database/repository.py` | DatasetRepository + OperationalRepository | USED |
| `database/init_operational.py` | Operational DB schema creation | USED |

### Risk
| File | Purpose | Status |
|---|---|---|
| `risk/engine.py` | Deterministic risk scoring | USED |
| `risk/indicators.py` | Indicator detection | USED |
| `risk/features.py` | Base feature normalizer | USED |
| `risk/transaction_features.py` | Transaction feature extraction | USED |
| `risk/profile_features.py` | Profile feature extraction | USED |
| `risk/chain_features.py` | Chain feature extraction | USED |
| `risk/atm_features.py` | ATM feature extraction | USED |
| `risk/geographic_features.py` | Geographic feature extraction | USED |

### Evidence
| File | Purpose | Status |
|---|---|---|
| `evidence/models.py` | EvidenceItem, EvidenceClassification | USED |
| `evidence/validator.py` | EvidenceValidator with provenance checks | USED |
| `evidence/collector.py` | EvidenceCollector factories | USED |
| `evidence/deduplicator.py` | EvidenceDeduplicator | USED |
| `evidence/formatter.py` | EvidenceFormatter | MARGINAL — only used in reporting |

### Reporting
| File | Purpose | Status |
|---|---|---|
| `reporting/models.py` | Report Pydantic models | USED |
| `reporting/builder.py` | ReportBuilder | USED |
| `reporting/pdf_generator.py` | ReportLab PDF engine | USED |
| `reporting/hasher.py` | SHA-256 hash | USED |
| `reporting/service.py` | ReportService orchestration | USED |
| `reporting/explainability.py` | ExplainabilityService (deterministic) | USED |

### Other Active
| File | Purpose | Status |
|---|---|---|
| `cli/main.py` | CLI commands | USED |
| `api/main.py` | FastAPI endpoints | USED |
| `api/models.py` | API Pydantic request/response | USED |
| `security/sanitizer.py` | PII sanitization | USED |
| `remediation/engine.py` | Remediation mappings | USED |
| `evaluation/engine.py` | Deterministic evaluation metrics | USED |
| `config.py` | Configuration | USED |
| `logger.py` | Logger setup | USED |

---

## Files That Are Obsolete / Can Be Cleaned

| File | Reason |
|---|---|
| `agent/llm_provider.py` | Stub — returns `LLM_UNAVAILABLE` for every method. Needs replacement with real Mistral client. |
| `scripts/db_corruption_report.py` | Diagnostic only. Not used in production. |
| `scripts/diagnose_db.py` | Diagnostic only. |
| `scripts/identify_corruption.py` | Diagnostic only. |
| `scripts/probe_scenario_data.py` | Diagnostic only. |
| `scripts/test_table_reads.py` | Diagnostic only. |
| `test_scenario.json` | Root-level leftover test fixture. Not imported anywhere. |
| `docs/agent_code_learning.md` | Internal learning notes. Not production docs. |
| `docs/agent_workflow_diagram.md` | Outdated. Superseded by ARCHITECTURE.md. |
| `docs/langgraph_architecture_over.md` | Outdated. |
| `docs/rea_api_system.md` | Outdated. |
| `docs/presentation.md` | Phase-era presentation notes. |
| `PHASE_6_AUDIT.md` | Superseded by this document. |
| `PHASE_6_COMPLETION_REPORT.md` | Phase-era report. |
| `PHASE_6_REGRESSION_FIX.md` | Phase-era regression report. |

---

## Current Execution Flow

```
python -m cli.main investigate scenario <SCENARIO_ID>
    → cmd_investigate()
    → PredictiveCybercrimeAgent.run(scenario_id)
        → DatasetRepository.get_scenario()  [validation]
        → LangGraph stream():
            observe_node  → hypothesize_node → planner_node → tool_execution_node → evaluate_node
            (loops until STOP or max_iterations)
        → EvidenceCollector.from_*()  [per tool result]
        → OperationalRepository.save_evidence()
        → RiskEngine.generate_finding()
        → RiskEngine.calculate_risk()
    → [user runs: python -m cli.main report investigation <ID>]
        → ReportService.create_report()
        → PDFGenerator.generate()
        → ReportHasher.hash_file()
```

---

## Database Flow

```
Master Dataset (READ-ONLY, ?mode=ro):
  data/synthetic/CYBER_INTERCEPT_FULL_DATASET/cyber_intercept.db
  Tables: transactions, profiles, atms, scenarios, districts, state_stats

Operational DB (READ-WRITE):
  data/agent/agent.db
  Tables: agent_sessions, investigations, observations, hypotheses,
          agent_decisions, findings, audit_events, risk_assessments,
          evidence_items, reports, finding_transitions
```

---

## Known Dataset Corruption (CRITICAL)

| Table/Column | Status | Impact |
|---|---|---|
| `transactions` | ✅ 40,005 rows — readable | Full chain tracing works |
| `profiles` | ✅ 18,404 rows — readable | Profile analysis works |
| `scenarios` (metadata cols) | ✅ 5 rows — readable | Case validation works |
| `scenarios.data_json` | ❌ CORRUPTED (UTF-8 malformed) | Cannot read structured entity data embedded in JSON |
| `atms` (table rows) | ❌ MALFORMED disk image | ATM data unreadable |
| `districts` | ✅ 533 rows — readable | Geographic lookups work |
| `state_stats` | ✅ 36 rows — readable | Risk geo-context works |

**Consequence**: The agent can trace full transaction chains and profile risk but cannot read ATM cashout location details and cannot use embedded scenario entity JSON from `data_json`. Account IDs must be discovered directly from transactions.

---

## LLM Flow — CURRENT (STUB)

```
LLMProvider(available=False)
    → generate_observation() → "LLM_UNAVAILABLE"
    → generate_hypothesis() → {"error": "LLM_UNAVAILABLE"}
    → rank_actions() → "LLM_UNAVAILABLE"
    → summarize_evidence() → "LLM_UNAVAILABLE"
```
All LLM calls fall through to deterministic rules in nodes.py.

---

## LLM Flow — REQUIRED

```
MistralClient(api_key=MISTRAL_API_KEY)
    → structured prompt with evidence context
    → parse structured JSON response
    → validate: no invented facts, no risk score changes
    → use for: hypothesis, action ranking, finding explanation, executive summary
```

---

## Remaining Bugs

1. **`scenarios.data_json` corrupt** — `get_scenario_raw()` currently tries `SELECT *` which includes `data_json`, causing a UTF-8 decode error. The query must exclude `data_json` or use `text_factory` workaround.
2. **ATM table malformed** — `get_atm()` will crash. Needs graceful error handling + BLOCKED status.
3. **`LLMProvider` is a stub** — Needs real Mistral API integration via `llm/client.py`.
4. **CLI `investigate`** currently requires pre-known scenario_id as argument. Needs interactive mode with victim validation.
5. **`get_scenario_raw`** passes `*` including corrupt `data_json` — entities like victim accounts cannot be reliably extracted.
6. **Report is decoupled from investigation** — User must separately run `report investigation` after investigation. Should be unified.
7. **Money flow not displayed in CLI** — Terminal output only shows raw findings, not structured transaction chain visualization.

---

## Technical Debt

1. `agent/llm_provider.py` stub must be replaced by real `llm/` package.
2. CLI needs interactive mode (not just `investigate scenario <ID>`).
3. `data_json` in scenarios needs safe selective extraction (avoid corrupt column).
4. Report generation is manual — should auto-generate after investigation completes.
5. No victim validation logic exists.
6. Money flow display (hop-by-hop chain) missing from CLI output.
7. `reporting/builder.py` has `SYNTHETIC_DEMO` path that should be removed from the production flow.

---

## Missing Production-Readiness Components

1. **`llm/` package** — Mistral client, structured prompts, response validator
2. **Interactive CLI** — Case/victim input, validation, confirmation
3. **Unified investigation + reporting** — Single command produces PDF
4. **Money flow visualization** in CLI
5. **ATM graceful degradation** — BLOCKED message when ATM data is unreadable
6. **`data_json` safe reading** — SELECT only non-corrupt columns
7. **`FINAL_ARCHITECTURE_AUDIT.md`** — This document
