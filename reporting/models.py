"""
reporting/models.py — Report data models, enums, and lifecycle types.
"""

import uuid
from datetime import datetime, UTC
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, field_validator


class ReportMode(str, Enum):
    REAL           = "REAL"            # Against live (non-corrupted) master DB
    SYNTHETIC_DEMO = "SYNTHETIC_DEMO"  # Deterministic fixture data — clearly labelled
    BLOCKED        = "BLOCKED"         # Real data requested but inaccessible


class FindingLifecycleStatus(str, Enum):
    OPEN         = "OPEN"          # Initial state — no review yet
    UNDER_REVIEW = "UNDER_REVIEW"  # Under manual expert review
    SUPPORTED    = "SUPPORTED"     # Evidence supports the finding
    INCONCLUSIVE = "INCONCLUSIVE"  # Contradictory evidence — cannot conclude
    REJECTED     = "REJECTED"      # Evidence does not support; finding dismissed
    CLOSED       = "CLOSED"        # Investigation closed; no further action


class ValidationStatus(str, Enum):
    PASS    = "PASS"
    FAIL    = "FAIL"
    BLOCKED = "BLOCKED"


# ── Finding Full Model (Phase 5 extended) ────────────────────────────────────

class FindingModel(BaseModel):
    finding_id:       str
    investigation_id: str
    title:            str
    category:         str
    description:      str
    severity:         str   # LOW / MODERATE / HIGH / CRITICAL
    risk_score:       float
    confidence:       float
    status:           FindingLifecycleStatus
    indicator_ids:    List[str]
    evidence_ids:     List[str]
    recommendations:  List[Dict[str, Any]]
    created_at:       str
    updated_at:       str
    machine_readable: Optional[Dict[str, Any]] = None

    @field_validator("risk_score")
    @classmethod
    def risk_score_range(cls, v: float) -> float:
        if not (0.0 <= v <= 100.0):
            raise ValueError(f"risk_score must be in [0, 100], got {v}")
        return v


# ── Audit Trail Item ─────────────────────────────────────────────────────────

class AuditEventModel(BaseModel):
    event_id:         str
    investigation_id: str
    event_type:       str
    timestamp:        str
    component:        str
    status:           str
    metadata:         Dict[str, Any]


# ── Data Source Status ───────────────────────────────────────────────────────

class DataSourceStatus(BaseModel):
    source_name:  str                     # e.g. "transactions", "profiles"
    status:       ValidationStatus
    row_count:    Optional[int] = None
    reason:       Optional[str] = None    # If BLOCKED or FAIL, why


# ── Full Report Model ────────────────────────────────────────────────────────

class SecurityAssessmentReport(BaseModel):
    # Identity
    report_id:           str
    investigation_id:    str
    scenario_id:         str
    generated_at:        str
    mode:                ReportMode

    # Sections
    executive_summary:   str
    scope:               str
    methodology:         str
    data_sources:        List[DataSourceStatus]
    investigation_summary: str

    # Subject Analysis
    subjects:            List[str]          # Masked account IDs
    transaction_analysis: str
    geographic_analysis:  str
    money_flow_chains:   List[Dict[str, Any]] = []
    atm_analysis_status: str = ""

    # Intelligence
    indicators:          List[Dict[str, Any]]
    findings:            List[FindingModel]
    risk_assessment:     Dict[str, Any]     # risk_score, risk_level, confidence
    evidence:            List[Dict[str, Any]]  # Formatted EvidenceItem dicts
    recommendations:     List[Dict[str, Any]]

    # Meta
    limitations:         str
    audit_summary:       List[AuditEventModel]
    validation_status:   Dict[str, ValidationStatus]

    # Integrity
    report_hash:         Optional[str] = None  # SHA-256 of PDF; set after generation
    pdf_path:            Optional[str] = None

    @classmethod
    def create_empty(
        cls,
        investigation_id: str,
        scenario_id: str,
        mode: ReportMode,
    ) -> "SecurityAssessmentReport":
        now = datetime.now(UTC).isoformat()
        return cls(
            report_id=str(uuid.uuid4()),
            investigation_id=investigation_id,
            scenario_id=scenario_id,
            generated_at=now,
            mode=mode,
            executive_summary="",
            scope="",
            methodology="",
            data_sources=[],
            investigation_summary="",
            subjects=[],
            transaction_analysis="",
            geographic_analysis="",
            money_flow_chains=[],
            atm_analysis_status="",
            indicators=[],
            findings=[],
            risk_assessment={},
            evidence=[],
            recommendations=[],
            limitations="",
            audit_summary=[],
            validation_status={},
        )


# ── Report Record (persisted metadata) ───────────────────────────────────────

class ReportRecord(BaseModel):
    report_id:        str
    investigation_id: str
    scenario_id:      str
    mode:             str
    pdf_path:         str
    sha256:           str
    generated_at:     str


# ── Finding Lifecycle Transition ─────────────────────────────────────────────

class FindingTransition(BaseModel):
    transition_id:    str
    finding_id:       str
    investigation_id: str
    from_status:      str
    to_status:        str
    reason:           str
    transitioned_at:  str
    transitioned_by:  str  # component name — never exposes user credentials
