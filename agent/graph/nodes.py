from typing import Dict, Any
from .state import InvestigationState
from ..tools import registry

def ingest_complaint(state: InvestigationState) -> Dict[str, Any]:
    print("[AGENT] Ingesting complaint...")
    res = registry.get_complaint(state["case_id"])
    if res.success:
        return {"complaint": res.data, "current_account": res.data.get("victim_account")}
    return {"errors": [{"step": "ingest_complaint", "error": res.error}]}

def analyze_complaint(state: InvestigationState) -> Dict[str, Any]:
    print("[AGENT] Analyzing complaint...")
    return {"investigation_status": "ANALYZING"}

def fetch_account(state: InvestigationState) -> Dict[str, Any]:
    print(f"[AGENT] Fetching account: {state.get('current_account')}")
    res = registry.get_account_transactions(state.get("current_account"))
    if res.success:
        return {"evidence": state.get("evidence", []) + [res.data]}
    return {}

def trace_transactions(state: InvestigationState) -> Dict[str, Any]:
    print("[AGENT] Tracing transaction graph...")
    res = registry.trace_transaction_graph(state.get("current_account"))
    if res.success and res.data.get("paths"):
        path = res.data["paths"][0]["path"]
        suspicious = [acct for acct in path if acct != state.get("current_account") and acct != path[1]]
        return {"transaction_paths": res.data["paths"], "suspicious_accounts": suspicious}
    return {}

def assess_account_risk(state: InvestigationState) -> Dict[str, Any]:
    print("[AGENT] Assessing account risk...")
    suspicious = state.get("suspicious_accounts", [])
    if suspicious:
        res = registry.calculate_account_risk(suspicious[0])
        return {"risk_score": res.data.get("risk_score")}
    return {}

def check_withdrawals(state: InvestigationState) -> Dict[str, Any]:
    print("[AGENT] Checking withdrawals...")
    return {"investigation_status": "CHECKING_WITHDRAWALS"}

def geo_analysis(state: InvestigationState) -> Dict[str, Any]:
    print("[AGENT] Performing geographic analysis...")
    return {"investigation_status": "GEO_ANALYSIS"}

def predict_withdrawal(state: InvestigationState) -> Dict[str, Any]:
    print("[AGENT] Predicting withdrawal location...")
    res = registry.predict_withdrawal_location()
    return {"predictions": res.data.get("predictions", [])}

def verify_evidence(state: InvestigationState) -> Dict[str, Any]:
    print("[AGENT] Verifying evidence...")
    res = registry.verify_evidence(state.get("evidence", []))
    return {"confidence": 0.95} if res.success else {"confidence": 0.5}

def risk_fusion(state: InvestigationState) -> Dict[str, Any]:
    print("[AGENT] Performing risk fusion...")
    return {"investigation_status": "RISK_FUSION"}

def report(state: InvestigationState) -> Dict[str, Any]:
    print("[AGENT] Generating report...")
    res = registry.generate_report(state["case_id"], state.get("evidence"))
    return {"investigation_status": "REPORT_GENERATED"}

def audit(state: InvestigationState) -> Dict[str, Any]:
    print("[AGENT] Recording audit event...")
    return {"investigation_status": "AUDITED"}
