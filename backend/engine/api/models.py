"""
api/models.py — Pydantic request / response models for the FastAPI routes.
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any


# ── Internal investigation routes ────────────────────────────────────────────

class InvestigationRequest(BaseModel):
    scenario_id: str
    max_iterations: int = 15
    max_tool_calls: int = 20


class InvestigationResponse(BaseModel):
    investigation_id: str
    scenario_id: str
    status: str
    message: str
    report_id: Optional[str] = None


class SystemStatusResponse(BaseModel):
    version: str
    python_version: str
    dataset_db_available: bool
    operational_db_available: bool
    dataset_db_readonly: bool
    registered_tools: int
    reporting_available: bool


class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None


# ── Frontend-compatible /api/* routes ────────────────────────────────────────

class InvestigateRunRequest(BaseModel):
    """Body for POST /api/investigate/run — mirrors api.ts `runInvestigation`."""
    scenarioId: str


class ScenarioDataResponse(BaseModel):
    """
    Mirrors the TypeScript `ScenarioData` interface in frontend/src/services/api.ts.
    The agent's final_state is mapped to this shape by `_map_state_to_scenario()`.
    """
    id: str
    title: str
    description: str
    verdict: str                              # UNANIMOUS_FRAUD_INTERCEPT | LEGITIMATE_... | BORDERLINE_...
    riskLevel: str                            # CRITICAL | HIGH | MEDIUM | LOW | SAFE
    overallRisk: float
    swarmWeights: Dict[str, float]            # {financial, forensic, geoSpatial}
    expectedWindow: float                     # hours until cashout
    predictedAtms: List[Dict[str, Any]]       # [{id, name, lat, lng, riskScore, probability}]
    networkNodes: List[Dict[str, Any]]        # [{id, label, riskType, details?}]
    networkEdges: List[Dict[str, Any]]        # [{source, target, amount, riskType, timestamp?}]
    bankIntervention: Dict[str, Any]          # {required, status, amount?, refId?}
    leaIntervention: Dict[str, Any]           # {required, status, unit?, eta?}
    # Agent-specific extras (not rendered by frontend but useful for debugging)
    agentStatus: Optional[str] = None
    stopReason: Optional[str] = None
    investigationId: Optional[str] = None
    iterationsUsed: Optional[int] = None
    toolCallsUsed: Optional[int] = None
    findingsCount: Optional[int] = None
    evidenceCount: Optional[int] = None


class MacroStatsResponse(BaseModel):
    """Mirrors `MacroStats` in api.ts."""
    activeInvestigations: int
    highRiskAlerts: int
    successfulInterventions: int


class InterlockRequest(BaseModel):
    accountId: str


class InterlockResponse(BaseModel):
    status: str
    detail: Optional[str] = None


class DossierRequest(BaseModel):
    caseId: str


class DossierResponse(BaseModel):
    url: str
