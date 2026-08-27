import pytest
from agent.graph.state import InvestigationState
from agent.graph.nodes import planner_node, evaluate_node, observe_node

def create_base_state() -> InvestigationState:
    return {
        "session_id": "test-session",
        "investigation_id": "test-inv",
        "scenario_id": "SCENARIO_TEST",
        "objective": "Test objective",
        "current_subject": None,
        "subjects_discovered": [],
        "accounts": [],
        "transactions": [],
        "transaction_chains": [],
        "profiles": [],
        "atms": [],
        "observations": [],
        "hypotheses": [],
        "evidence": [],
        "findings": [],
        "completed_tools": [],
        "pending_actions": [],
        "tool_args": {},
        "tool_history": [],
        "decision_history": [],
        "iteration": 1,
        "max_iterations": 15,
        "confidence": None,
        "risk_score": None,
        "status": "INITIALIZED",
        "stop_reason": None
    }

def test_planner_scenario_context():
    state = create_base_state()
    updates = planner_node(state)
    assert updates["pending_actions"][0] == "get_scenario_raw"
    assert updates["tool_args"]["scenario_id"] == "SCENARIO_TEST"

def test_planner_search_transactions():
    state = create_base_state()
    state["completed_tools"] = ["get_scenario_raw"]
    state["accounts"] = ["ACC-123"]
    state["profiles"] = [{"account_id": "ACC-123", "risk_score": 0.8}]
    updates = planner_node(state)
    assert updates["pending_actions"][0] == "search_transactions"
    assert updates["tool_args"]["from_account"] == "ACC-123"

def test_planner_trace_transaction_chain():
    state = create_base_state()
    state["completed_tools"] = ["get_scenario_raw", "get_profile", "search_transactions"]
    state["accounts"] = ["ACC-123"]
    state["profiles"] = [{"account_id": "ACC-123", "risk_score": 0.8}]
    state["transactions"] = [{"transaction_id": "TXN-123"}]
    updates = planner_node(state)
    assert updates["pending_actions"][0] == "get_transaction_chain"
    # This regression test proves the tracing node receives a valid identifier
    assert updates["tool_args"]["chain_id"] == "TXN-123"
    assert updates["tool_args"]["chain_id"] is not None

def test_loop_detection():
    state = create_base_state()
    # Simulate same tool called 3 times
    state["tool_history"] = [
        {"tool_name": "search_transactions"},
        {"tool_name": "search_transactions"},
        {"tool_name": "search_transactions"}
    ]
    updates = observe_node(state)
    assert updates.get("stop_reason") == "AGENT_LOOP_DETECTED"
    
def test_evaluate_prevents_duplicate_findings(mocker):
    # Mock RiskEngine to return a finding
    mocker.patch("risk.engine.RiskEngine.generate_finding", return_value={"title": "Test Finding", "finding_id": "find-1", "category": "LAUNDERING", "severity": "HIGH", "confidence": 0.9, "description": "Test", "evidence_ids": [], "remediation": "Test", "status": "CONFIRMED"})
    mocker.patch("risk.engine.RiskEngine.calculate_risk", return_value={"risk_score": 0.9, "risk_level": "HIGH", "confidence": 0.9, "indicators": []})
    
    state = create_base_state()
    state["tool_history"] = [{"tool_name": "test_tool", "success": True, "data": "test"}]
    
    # First time, finding is added
    updates = evaluate_node(state)
    assert len(updates.get("findings", [])) == 1
    assert updates["findings"][0]["title"] == "Test Finding"
    
    # Second time, state already has finding with same title
    state["findings"] = [{"title": "Test Finding"}]
    updates2 = evaluate_node(state)
    assert "findings" not in updates2 # Should not add duplicate
