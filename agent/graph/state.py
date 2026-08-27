from typing import TypedDict, List, Dict, Any, Optional, Annotated
import operator

class InvestigationState(TypedDict):
    """
    State for dynamic agentic investigation.
    """
    session_id: Optional[str]
    investigation_id: Optional[str]
    scenario_id: str
    objective: str
    current_subject: Optional[str]
    subjects_discovered: Annotated[List[str], operator.add]
    
    # DB Entity Caches (sanitized models stored as dicts)
    accounts: Annotated[List[str], operator.add]
    transactions: Annotated[List[Dict[str, Any]], operator.add]
    transaction_chains: Annotated[List[Dict[str, Any]], operator.add]
    profiles: Annotated[List[Dict[str, Any]], operator.add]
    atms: Annotated[List[Dict[str, Any]], operator.add]
    
    # Dynamic Agent State
    observations: Annotated[List[Dict[str, Any]], operator.add]
    hypotheses: Annotated[List[Dict[str, Any]], operator.add]
    evidence: Annotated[List[Dict[str, Any]], operator.add]
    findings: Annotated[List[Dict[str, Any]], operator.add]
    
    # Execution Tracking
    completed_tools: Annotated[List[str], operator.add]
    pending_actions: List[str]  # Overwrite each iteration
    tool_args: Dict[str, Any]   # Overwrite each iteration
    tool_history: Annotated[List[Dict[str, Any]], operator.add]
    decision_history: Annotated[List[Dict[str, Any]], operator.add]
    
    iteration: int
    max_iterations: int
    confidence: Optional[float]
    risk_score: Optional[float]
    status: str
    stop_reason: Optional[str]
