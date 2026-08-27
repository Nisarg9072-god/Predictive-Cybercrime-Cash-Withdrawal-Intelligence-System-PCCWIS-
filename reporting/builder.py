"""
reporting/builder.py — Orchestrates the evidence-to-report pipeline.

Modes:
  REAL           — uses agent state from real investigation (may be BLOCKED)
  SYNTHETIC_DEMO — uses deterministic synthetic fixtures; clearly labelled
  BLOCKED        — real data requested but inaccessible due to corruption

Evidence and synthetic data are NEVER mixed within the same report.
"""

import uuid
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

from evidence.collector import EvidenceCollector
from evidence.deduplicator import EvidenceDeduplicator
from evidence.formatter import EvidenceFormatter
from evidence.models import EvidenceClassification, EvidenceItem
from evidence.validator import EvidenceValidator
from remediation.engine import RemediationEngine
from reporting.explainability import ExplainabilityService
from reporting.models import (
    AuditEventModel, DataSourceStatus, FindingLifecycleStatus, FindingModel,
    ReportMode, SecurityAssessmentReport, ValidationStatus,
)
from risk.engine import RiskEngine
from security.sanitizer import Sanitizer


def _now() -> str:
    return datetime.now(UTC).isoformat()


# ── Synthetic Fixture ─────────────────────────────────────────────────────────

SYNTHETIC_STATE = {
    "investigation_id": "SYNTH-INV-001",
    "scenario_id":      "SYNTHETIC_SCENARIO",
    "iteration":        5,
    "accounts": ["ACC_SYNTH_0001", "ACC_SYNTH_0002", "ACC_SYNTH_0003"],
    "transactions": [
        {
            "txn_id": "TXN_SYNTH_001", "chain_id": "CHAIN_SYNTH_001",
            "pattern_type": "STACK", "timestamp_ist": "2026-01-01 10:00:00 IST",
            "from_account_id": "ACC_SYNTH_0001", "from_bank": "Demo Bank A",
            "to_account_id": "ACC_SYNTH_0002", "to_bank": "Demo Bank B",
            "amount_inr": 75000.0, "channel": "UPI",
            "is_laundering": 1, "hop_layer": 0, "is_terminal_cashout": 0,
            "crime_category": "SYNTHETIC_TEST",
        },
        {
            "txn_id": "TXN_SYNTH_002", "chain_id": "CHAIN_SYNTH_001",
            "pattern_type": "STACK", "timestamp_ist": "2026-01-01 10:05:00 IST",
            "from_account_id": "ACC_SYNTH_0002", "from_bank": "Demo Bank B",
            "to_account_id": "ACC_SYNTH_0003", "to_bank": "Demo Bank C",
            "amount_inr": 70000.0, "channel": "IMPS",
            "is_laundering": 1, "hop_layer": 1, "is_terminal_cashout": 0,
            "crime_category": "SYNTHETIC_TEST",
        },
        {
            "txn_id": "TXN_SYNTH_003", "chain_id": "CHAIN_SYNTH_001",
            "pattern_type": "STACK", "timestamp_ist": "2026-01-01 10:10:00 IST",
            "from_account_id": "ACC_SYNTH_0003", "from_bank": "Demo Bank C",
            "to_account_id": "ACC_SYNTH_0004", "to_bank": "Demo Bank D",
            "amount_inr": 65000.0, "channel": "NEFT",
            "is_laundering": 1, "hop_layer": 2, "is_terminal_cashout": 1,
            "crime_category": "SYNTHETIC_TEST",
        },
    ],
    "profiles": [
        {
            "profile_id": "PROF_SYNTH_001", "account_id": "ACC_SYNTH_0001",
            "holder_name": "SYNTHETIC USER A", "bank_name": "Demo Bank A",
            "kyc_status": "VERIFIED", "account_age_days": 15,
            "risk_score": 80.0, "is_mule": 1, "mule_type": "SYNTHETIC",
            "last_known_city": "Demo City", "last_known_state": "Demo State",
            "withdrawal_velocity_per_day": 75000.0,
        },
    ],
    "transaction_chains": [
        {
            "chain_id": "CHAIN_SYNTH_001", "pattern_type": "STACK",
            "total_amount": 210000.0, "hop_count": 3, "transactions": [],
        },
    ],
    "atms": [],
    "evidence": [],
    "stop_reason": "AGENT_DECIDED_STOP",
}


class ReportBuilder:
    """Builds a SecurityAssessmentReport from investigation state or synthetic data."""

    @classmethod
    def build(
        cls,
        investigation_id: str,
        scenario_id: str,
        mode: ReportMode,
        agent_state: Optional[Dict[str, Any]] = None,
        audit_events: Optional[List[Dict]] = None,
    ) -> SecurityAssessmentReport:
        if mode == ReportMode.SYNTHETIC_DEMO:
            return cls._build_synthetic(investigation_id, scenario_id)
        if mode == ReportMode.BLOCKED:
            return cls._build_blocked(investigation_id, scenario_id)
        # REAL mode
        if not agent_state:
            return cls._build_blocked(investigation_id, scenario_id)
        return cls._build_real(investigation_id, scenario_id, agent_state, audit_events or [])

    # ── SYNTHETIC ────────────────────────────────────────────────────────────

    @classmethod
    def _build_synthetic(
        cls, investigation_id: str, scenario_id: str
    ) -> SecurityAssessmentReport:
        state = {**SYNTHETIC_STATE, "investigation_id": investigation_id, "scenario_id": scenario_id}
        report = SecurityAssessmentReport.create_empty(investigation_id, scenario_id, ReportMode.SYNTHETIC_DEMO)

        # Collect SYNTHETIC evidence
        evidence_items: List[EvidenceItem] = []
        for tx in state["transactions"]:
            for ev in EvidenceCollector.from_transactions(investigation_id, state["transactions"]):
                ev = ev.model_copy(update={"classification": EvidenceClassification.SYNTHETIC})
                evidence_items.append(ev)
            break  # only once
        for prof in state["profiles"]:
            for ev in EvidenceCollector.from_profile(investigation_id, prof):
                ev = ev.model_copy(update={"classification": EvidenceClassification.SYNTHETIC})
                evidence_items.append(ev)
        for ev in EvidenceCollector.from_chain(investigation_id, state["transactions"]):
            ev = ev.model_copy(update={"classification": EvidenceClassification.SYNTHETIC})
            evidence_items.append(ev)

        # Validate
        ok, errs = EvidenceValidator.validate_batch(evidence_items)

        # Deduplicate
        unique_evidence, _ = EvidenceDeduplicator.deduplicate(evidence_items, [])

        # Risk calculation
        risk_analysis = RiskEngine.calculate_risk(state)

        # Findings
        raw_finding = RiskEngine.generate_finding(state)
        findings: List[FindingModel] = []
        if raw_finding:
            recs = RemediationEngine.get_recommendations(raw_finding["category"])
            ev_ids = [e.evidence_id for e in unique_evidence]
            explanation = ExplainabilityService.explain_finding(
                finding_id=raw_finding["finding_id"],
                title=raw_finding["title"],
                category=raw_finding["category"],
                severity=raw_finding["severity"],
                risk_score=raw_finding["risk_score"],
                confidence=raw_finding["confidence"],
                status=raw_finding["status"],
                indicators=risk_analysis["indicators"],
                evidence_items=unique_evidence,
            )
            findings.append(FindingModel(
                finding_id=raw_finding["finding_id"],
                investigation_id=investigation_id,
                title="[SYNTHETIC] " + raw_finding["title"],
                category=raw_finding["category"],
                description=explanation["prose"],
                severity=raw_finding["severity"],
                risk_score=raw_finding["risk_score"],
                confidence=raw_finding["confidence"],
                status=FindingLifecycleStatus.OPEN,
                indicator_ids=[ind["indicator_id"] for ind in risk_analysis["indicators"]],
                evidence_ids=ev_ids,
                recommendations=recs,
                created_at=_now(),
                updated_at=_now(),
                machine_readable=raw_finding.get("machine_readable"),
            ))

        # Build report
        report.executive_summary = cls._synthetic_exec_summary(state, risk_analysis, len(findings))
        report.scope = "Synthetic demonstration scenario. No real subjects or transactions."
        report.methodology = cls._methodology_text()
        report.data_sources = [
            DataSourceStatus(source_name="SYNTHETIC_FIXTURE", status=ValidationStatus.PASS, row_count=len(state["transactions"]), reason="Deterministic test data")
        ]
        report.investigation_summary = (
            f"Synthetic investigation completed in {state['iteration']} iterations. "
            f"Identified {len(state['accounts'])} subject accounts and "
            f"{len(state['transactions'])} transactions."
        )
        report.subjects = [Sanitizer.mask_account_number(a) for a in state["accounts"]]
        report.transaction_analysis = cls._tx_analysis(state)
        report.geographic_analysis = "Geographic analysis not available in synthetic mode."
        report.money_flow_chains = state.get("transaction_chains", [])
        report.atm_analysis_status = "PASS"
        report.indicators = risk_analysis["indicators"]
        report.findings = findings
        report.risk_assessment = {
            "risk_score": risk_analysis["risk_score"],
            "risk_level": risk_analysis["risk_level"],
            "confidence": risk_analysis["confidence"],
            "contradictory_evidence": risk_analysis["contradictory_evidence"],
        }
        report.evidence = EvidenceFormatter.format_list_for_pdf(unique_evidence)
        report.recommendations = RemediationEngine.get_recommendations(
            findings[0].category if findings else "UNUSUAL_TRANSACTION_PATTERN"
        )
        report.limitations = (
            "SYNTHETIC DATA: This report was generated from deterministic test fixtures. "
            "It does not represent a real investigation and must not be used for any legal or enforcement purpose."
        )
        report.audit_summary = [AuditEventModel(
            event_id=str(uuid.uuid4()),
            investigation_id=investigation_id,
            event_type="REPORT_GENERATED",
            timestamp=_now(),
            component="ReportBuilder",
            status="SUCCESS",
            metadata={"mode": "SYNTHETIC_DEMO"},
        )]
        report.validation_status = {
            "unit_tests":    ValidationStatus.PASS,
            "operational_db": ValidationStatus.PASS,
            "master_db":     ValidationStatus.BLOCKED,
            "real_e2e":      ValidationStatus.BLOCKED,
        }
        return report

    # ── BLOCKED ──────────────────────────────────────────────────────────────

    @classmethod
    def _build_blocked(
        cls, investigation_id: str, scenario_id: str
    ) -> SecurityAssessmentReport:
        report = SecurityAssessmentReport.create_empty(investigation_id, scenario_id, ReportMode.BLOCKED)
        report.executive_summary = (
            "INVESTIGATION BLOCKED\n\n"
            "The requested investigation could not be completed because required data sources "
            "are inaccessible due to database corruption.\n\n"
            "Master Database Health: FAIL\n"
            "Real Scenario E2E: BLOCKED\n"
            "Reason: profiles and atms tables inaccessible (B-tree index corruption on idx_atms_geo).\n\n"
            "Do not interpret the absence of findings as evidence of absence of risk."
        )
        report.scope = f"Scenario {scenario_id}"
        report.methodology = cls._methodology_text()
        report.data_sources = [
            DataSourceStatus(source_name="profiles", status=ValidationStatus.BLOCKED, reason="B-tree page corruption — all row reads fail"),
            DataSourceStatus(source_name="atms",     status=ValidationStatus.BLOCKED, reason="B-tree page corruption — all row reads fail"),
            DataSourceStatus(source_name="transactions", status=ValidationStatus.FAIL, reason="Partial — crime_category index corrupted"),
            DataSourceStatus(source_name="scenarios",    status=ValidationStatus.PASS, row_count=5),
        ]
        report.money_flow_chains = []
        report.atm_analysis_status = "BLOCKED"
        report.limitations = (
            "The master database (12 GB) has confirmed B-tree page corruption in index idx_atms_geo "
            "(root page 29). This prevents reading the profiles and atms tables. The data_json "
            "field on scenarios is also corrupt and cannot be parsed. No findings can be generated "
            "without access to profile and transaction chain data. The master database must NOT "
            "be modified or repaired."
        )
        report.validation_status = {
            "unit_tests":    ValidationStatus.PASS,
            "operational_db": ValidationStatus.PASS,
            "master_db":     ValidationStatus.FAIL,
            "real_e2e":      ValidationStatus.BLOCKED,
        }
        return report

    # ── REAL ─────────────────────────────────────────────────────────────────

    @classmethod
    def _build_real(
        cls,
        investigation_id: str,
        scenario_id: str,
        agent_state: Dict[str, Any],
        audit_events: List[Dict],
    ) -> SecurityAssessmentReport:
        report = SecurityAssessmentReport.create_empty(investigation_id, scenario_id, ReportMode.REAL)

        # Collect OBSERVED evidence
        evidence_items: List[EvidenceItem] = []
        if agent_state.get("transactions"):
            evidence_items.extend(EvidenceCollector.from_transactions(investigation_id, agent_state["transactions"]))
        for prof in agent_state.get("profiles", []):
            evidence_items.extend(EvidenceCollector.from_profile(investigation_id, prof if isinstance(prof, dict) else prof.model_dump()))
        if agent_state.get("transaction_chains"):
            txn_chain = [t if isinstance(t, dict) else t.model_dump() for t in agent_state.get("transactions", [])]
            evidence_items.extend(EvidenceCollector.from_chain(investigation_id, txn_chain))
        for atm in agent_state.get("atms", []):
            evidence_items.extend(EvidenceCollector.from_atm(investigation_id, atm if isinstance(atm, dict) else atm.model_dump()))

        unique_evidence, _ = EvidenceDeduplicator.deduplicate(evidence_items, [])
        risk_analysis = RiskEngine.calculate_risk(agent_state)
        
        findings: List[FindingModel] = []
        for raw_finding in agent_state.get("findings", []):
            recs = RemediationEngine.get_recommendations(raw_finding["category"])
            ev_ids = [e.evidence_id for e in unique_evidence]
            # If LLM explanation exists, use it. Else fallback to programmatic prose.
            if raw_finding.get("llm_explanation"):
                description = raw_finding["llm_explanation"]
            else:
                explanation = ExplainabilityService.explain_finding(
                    finding_id=raw_finding["finding_id"],
                    title=raw_finding["title"],
                    category=raw_finding["category"],
                    severity=raw_finding["severity"],
                    risk_score=raw_finding["risk_score"],
                    confidence=raw_finding["confidence"],
                    status=raw_finding["status"],
                    indicators=risk_analysis["indicators"],
                    evidence_items=unique_evidence,
                )
                description = explanation["prose"]

            findings.append(FindingModel(
                finding_id=raw_finding["finding_id"],
                investigation_id=investigation_id,
                title=raw_finding["title"],
                category=raw_finding["category"],
                description=description,
                severity=raw_finding["severity"],
                risk_score=raw_finding["risk_score"],
                confidence=raw_finding["confidence"],
                status=FindingLifecycleStatus.OPEN,
                indicator_ids=[ind["indicator_id"] for ind in risk_analysis["indicators"]],
                evidence_ids=ev_ids,
                recommendations=recs,
                created_at=_now(),
                updated_at=_now(),
                machine_readable=raw_finding.get("machine_readable"),
            ))

        llm_exec_summary = agent_state.get("llm_executive_summary")
        if llm_exec_summary:
            report.executive_summary = llm_exec_summary
        else:
            report.executive_summary = cls._real_exec_summary(agent_state, risk_analysis, len(findings))
        report.scope = f"Scenario {scenario_id}"
        report.methodology = cls._methodology_text()
        report.data_sources = cls._probe_data_sources()
        report.investigation_summary = (
            f"Investigation completed in {agent_state.get('iteration', 0)} iterations. "
            f"Stop reason: {agent_state.get('stop_reason', 'unknown')}."
        )
        report.subjects = [Sanitizer.mask_account_number(a) for a in agent_state.get("accounts", [])]
        report.transaction_analysis = cls._tx_analysis(agent_state)
        
        atm_blocked = any(e.get("observation", "") == "ATM_ANALYSIS_BLOCKED" for e in agent_state.get("evidence", []))
        if atm_blocked:
            report.atm_analysis_status = "BLOCKED"
            report.geographic_analysis = "Geographic data source BLOCKED (atms table inaccessible). Analysis skipped."
        else:
            report.atm_analysis_status = "PASS" if agent_state.get("atms") else "FAIL"
            report.geographic_analysis = "No ATM data analysed." if not agent_state.get("atms") else "ATM location analysed."
            
        report.money_flow_chains = agent_state.get("transaction_chains", [])
        report.indicators = risk_analysis["indicators"]
        report.findings = findings
        report.risk_assessment = {
            "risk_score": risk_analysis["risk_score"],
            "risk_level": risk_analysis["risk_level"],
            "confidence": risk_analysis["confidence"],
            "contradictory_evidence": risk_analysis["contradictory_evidence"],
        }
        report.evidence = EvidenceFormatter.format_list_for_pdf(unique_evidence)
        report.recommendations = RemediationEngine.get_recommendations(
            findings[0].category if findings else "UNUSUAL_TRANSACTION_PATTERN"
        )
        report.limitations = (
            "Master database corruption prevents access to profiles, atms, and transaction chain data. "
            "Risk assessment may be incomplete. Do not act on this report without additional data sources."
        )
        report.audit_summary = [
            AuditEventModel(
                event_id=str(uuid.uuid4()),
                investigation_id=investigation_id,
                event_type=ev.get("event_type", "AGENT_EVENT"),
                timestamp=ev.get("created_at", _now()),
                component=ev.get("component", "AGENT"),
                status=ev.get("status", "UNKNOWN"),
                metadata={k: v for k, v in ev.items() if k not in ("event_id", "session_id")},
            )
            for ev in audit_events
        ]
        if not audit_events:
            report.audit_summary = [AuditEventModel(
                event_id=str(uuid.uuid4()),
                investigation_id=investigation_id,
                event_type="INVESTIGATION_COMPLETED",
                timestamp=_now(),
                component="PredictiveCybercrimeAgent",
                status="COMPLETED",
                metadata={"stop_reason": agent_state.get("stop_reason", "unknown")},
            )]
        report.validation_status = {
            "unit_tests":    ValidationStatus.PASS,
            "operational_db": ValidationStatus.PASS,
            "master_db":     ValidationStatus.FAIL,
            "real_e2e":      ValidationStatus.BLOCKED,
        }
        return report

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _methodology_text() -> str:
        return (
            "This report was generated by the Predictive Cybercrime Cash Withdrawal Intelligence System (PCCWIS). "
            "Risk scores are computed by a deterministic, weighted indicator engine (Phase 4). "
            "Thresholds are PROJECT HEURISTICs and have not been statistically validated. "
            "Evidence is classified as OBSERVED, DERIVED, INFERRED, PREDICTED, or SYNTHETIC. "
            "No LLM was used to generate risk scores, severity, or confidence values. "
            "All findings require manual expert review before any enforcement action."
        )

    @staticmethod
    def _tx_analysis(state: Dict) -> str:
        txns = state.get("transactions", [])
        if not txns:
            return "No transaction data available."
        laundering = sum(1 for t in txns if (t.get("is_laundering") or (isinstance(t, dict) and t.get("is_laundering"))))
        cashouts   = sum(1 for t in txns if (t.get("is_terminal_cashout") or (isinstance(t, dict) and t.get("is_terminal_cashout"))))
        total      = sum(t.get("amount_inr", 0) for t in txns if isinstance(t, dict))
        return (
            f"Transactions analysed: {len(txns)}\n"
            f"Flagged as laundering: {laundering}\n"
            f"Terminal cashouts:     {cashouts}\n"
            f"Total value (INR):     {total:,.0f}"
        )

    @staticmethod
    def _synthetic_exec_summary(state: Dict, risk: Dict, n_findings: int) -> str:
        return (
            "⚠️  DEMONSTRATION REPORT — SYNTHETIC DATA — NOT REAL INVESTIGATION RESULTS\n\n"
            f"Objective:   Synthetic demonstration of the evidence-to-report pipeline.\n"
            f"Entities:    {len(state.get('accounts', []))} synthetic accounts investigated.\n"
            f"Transactions: {len(state.get('transactions', []))} synthetic transactions analysed.\n"
            f"Indicators:  {len(risk.get('indicators', []))} indicators triggered.\n"
            f"Findings:    {n_findings} finding(s) generated.\n"
            f"Risk Score:  {risk['risk_score']:.0f}/100 ({risk['risk_level']})\n"
            f"Confidence:  {risk['confidence']:.2f}\n\n"
            "Validation Limitations: Master DB is corrupted. Real data E2E is BLOCKED."
        )

    @staticmethod
    def _real_exec_summary(state: Dict, risk: Dict, n_findings: int) -> str:
        return (
            f"Objective:    Investigate cybercrime transaction pattern.\n"
            f"Entities:     {len(state.get('accounts', []))} accounts investigated.\n"
            f"Transactions: {len(state.get('transactions', []))} transactions analysed.\n"
            f"Indicators:   {len(risk.get('indicators', []))} indicators triggered.\n"
            f"Findings:     {n_findings} finding(s) generated.\n"
            f"Risk Score:   {risk['risk_score']:.0f}/100 ({risk['risk_level']})\n"
            f"Confidence:   {risk['confidence']:.2f}\n\n"
            "Validation Limitations: Master DB health FAIL. Real data E2E BLOCKED due to corruption."
        )

    @staticmethod
    def _probe_data_sources() -> List[DataSourceStatus]:
        import sqlite3, os
        db_path = "data/synthetic/CYBER_INTERCEPT_FULL_DATASET/cyber_intercept.db"
        sources = []
        if not os.path.exists(db_path):
            return [DataSourceStatus(source_name="master_db", status=ValidationStatus.FAIL, reason="File not found")]
        for table, probe_sql, label in [
            ("transactions", "SELECT count(*) FROM transactions WHERE is_terminal_cashout=1", "transactions"),
            ("profiles",     "SELECT profile_id FROM profiles LIMIT 1",                       "profiles"),
            ("scenarios",    "SELECT count(*) FROM scenarios",                                 "scenarios"),
            ("atms",         "SELECT atm_id FROM atms LIMIT 1",                               "atms"),
        ]:
            try:
                conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
                conn.text_factory = lambda b: b.decode(errors="replace")
                cur = conn.cursor()
                cur.execute(probe_sql)
                row = cur.fetchone()
                conn.close()
                status = ValidationStatus.PASS if row else ValidationStatus.FAIL
                sources.append(DataSourceStatus(source_name=label, status=status))
            except Exception as e:
                sources.append(DataSourceStatus(source_name=label, status=ValidationStatus.BLOCKED, reason=str(e)[:100]))
        return sources
