from agent.graph.state import InvestigationState

def test_state_creation():
    state: InvestigationState = {
        "case_id": "TEST-001",
        "session_id": "sess-1",
        "investigation_id": "inv-1",
        "complaint": {},
        "current_account": "ACC-123",
        "investigated_accounts": ["ACC-123"],
        "transaction_paths": [],
        "suspicious_accounts": [],
        "withdrawal_candidates": [],
        "predictions": [],
        "evidence": [],
        "risk_score": 0.5,
        "confidence": 0.9,
        "tool_calls": [],
        "alerts": [],
        "errors": [],
        "investigation_status": "TESTING",
        "iteration_count": 1
    }
    assert state["case_id"] == "TEST-001"
    assert state["risk_score"] == 0.5

