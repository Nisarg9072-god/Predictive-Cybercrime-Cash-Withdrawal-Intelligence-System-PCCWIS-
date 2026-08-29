from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, UTC
from enum import Enum

class InvestigationStatus(str, Enum):
    COMPLETED = "COMPLETED"
    INCONCLUSIVE = "INCONCLUSIVE"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"

class InvestigationResult(BaseModel):
    investigation_id: str
    scenario_id: str
    status: InvestigationStatus
    started_at: str
    completed_at: str
    iterations: int
    tool_calls: int
    
    observations: List[Dict[str, Any]] = Field(default_factory=list)
    hypotheses: List[Dict[str, Any]] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    indicators: List[Dict[str, Any]] = Field(default_factory=list)
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    risk_assessments: List[Dict[str, Any]] = Field(default_factory=list)
    remediation: List[Dict[str, Any]] = Field(default_factory=list)
    
    confidence: float = 0.0
    stop_reason: str = "Unknown"
    
    report_id: Optional[str] = None
    report_hash: Optional[str] = None

    @classmethod
    def from_state(cls, state: dict, status: InvestigationStatus, report_id: str = None, report_hash: str = None) -> "InvestigationResult":
        now = datetime.now(UTC).isoformat() + "Z"
        # Determine actual iterations and tool calls
        tool_history = state.get("tool_history", [])
        
        # Risk assessment
        risk_assessments = state.get("risk_assessments", [])
        confidence = 0.0
        if risk_assessments:
            confidence = risk_assessments[-1].get("confidence", 0.0)
            
        return cls(
            investigation_id=state.get("investigation_id", "UNKNOWN"),
            scenario_id=state.get("scenario_id", "UNKNOWN"),
            status=status,
            started_at=state.get("started_at", now),
            completed_at=now,
            iterations=state.get("iteration", 0),
            tool_calls=len(tool_history),
            observations=state.get("observations", []),
            hypotheses=state.get("hypotheses", []),
            evidence=state.get("evidence", []),
            indicators=state.get("indicators", []),
            findings=state.get("findings", []),
            risk_assessments=risk_assessments,
            remediation=state.get("remediation", []),
            confidence=confidence,
            stop_reason=state.get("stop_reason", "Completed gracefully"),
            report_id=report_id,
            report_hash=report_hash
        )
