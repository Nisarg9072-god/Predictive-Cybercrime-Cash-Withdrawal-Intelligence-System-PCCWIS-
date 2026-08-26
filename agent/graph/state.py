from typing import TypedDict, List, Dict, Any, Optional

class InvestigationState(TypedDict):
    """
    Shared contract for the LangGraph state.
    Every developer must use this structure.
    Do not add or remove fields without team consensus.
    """
    case_id: str
    complaint: Dict[str, Any]
    current_account: Optional[str]
    investigated_accounts: List[str]
    transaction_paths: List[Dict[str, Any]]
    suspicious_accounts: List[str]
    withdrawal_candidates: List[str]
    predictions: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]]
    risk_score: Optional[float]
    confidence: Optional[float]
    tool_calls: List[Dict[str, Any]]
    alerts: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]
    investigation_status: str
    iteration_count: int
