from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# ---------------------------------------------------------
# Sanitized Data Models (Dataset)
# ---------------------------------------------------------

class TransactionSummary(BaseModel):
    txn_id: str
    chain_id: Optional[str]
    pattern_type: Optional[str]
    timestamp_ist: str
    from_account_id: str
    from_bank: str
    to_account_id: str
    to_bank: str
    amount_inr: float
    channel: str
    is_laundering: int
    hop_layer: int
    is_terminal_cashout: int
    crime_category: Optional[str]

class ProfileSummary(BaseModel):
    profile_id: str
    account_id: str
    holder_name: str
    bank_name: str
    kyc_status: str
    account_age_days: int
    risk_score: float
    is_mule: int
    mule_type: Optional[str]
    last_known_city: Optional[str]
    last_known_state: Optional[str]
    withdrawal_velocity_per_day: float

class ATMRecord(BaseModel):
    atm_id: str
    bank_name: str
    atm_name: str
    latitude: float
    longitude: float
    state: str
    city: str
    atm_type: str
    is_24x7: int
    cash_availability_index: float
    operational_status: str

class ScenarioSummary(BaseModel):
    scenario_id: str
    scenario_name: str
    crime_category: str
    description: str
    victim_city: str
    victim_state: str
    amount_lost_inr: float
    status: str

class DistrictSummary(BaseModel):
    district_id: str
    district_name: str
    state_name: str
    centroid_lat: float
    centroid_lng: float

class StateRiskSummary(BaseModel):
    state_name: str
    total_incidents: int
    amount_reported_cr: float
    incident_density: float
    risk_tier: str

class TransactionChainSummary(BaseModel):
    chain_id: str
    pattern_type: str
    total_amount: float
    hop_count: int
    transactions: List[TransactionSummary]

# ---------------------------------------------------------
# Operational DB Models
# ---------------------------------------------------------

class AgentSession(BaseModel):
    session_id: str
    started_at: str
    completed_at: Optional[str] = None
    target_type: str
    target_id: str
    status: str
    iteration_count: int = 0
    tool_call_count: int = 0
    error: Optional[str] = None
    created_at: str

class Investigation(BaseModel):
    investigation_id: str
    session_id: str
    subject_type: str
    subject_id: str
    objective: str
    status: str
    started_at: str
    completed_at: Optional[str] = None

class Observation(BaseModel):
    observation_id: str
    investigation_id: str
    source: str
    observation_type: str
    summary: str
    confidence: float
    created_at: str

class Hypothesis(BaseModel):
    hypothesis_id: str
    investigation_id: str
    description: str
    category: str
    confidence: float
    status: str
    supporting_observations: str
    created_at: str
    updated_at: str

class AgentDecision(BaseModel):
    decision_id: str
    investigation_id: str
    iteration: int
    observation_summary: str
    selected_tool: str
    reason_summary: str
    result_summary: str
    created_at: str

class Finding(BaseModel):
    finding_id: str
    investigation_id: str
    title: str
    category: str
    severity: str
    confidence: float
    description: str
    evidence_summary: str
    remediation: str
    status: str
    created_at: str

class AuditEvent(BaseModel):
    event_id: str
    session_id: str
    event_type: str
    component: str
    status: str
    metadata: str
    created_at: str

class RiskAssessment(BaseModel):
    risk_assessment_id: str
    investigation_id: str
    iteration: int
    risk_score: float
    risk_level: str
    confidence: float
    indicator_ids: str
    evidence_ids: str
    created_at: str

