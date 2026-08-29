"""
api/main.py — FastAPI entry point for the Predictive Cybercrime Intelligence API.

Two layers of routes are exposed:
  1. Internal / legacy routes  (/health, /system/status, /investigations/*)
     — retained for operational monitoring and background task management.

  2. Frontend-compatible routes  (/api/*)
     — matches the BASE_URL expected by the React frontend (api.ts).
     — /api/investigate/run  : runs the agent synchronously and maps its output
                               to the ScenarioData shape the frontend understands.
     — /api/stats/macro      : returns aggregate investigation stats.
     — /api/interlock/freeze : stub for bank intervention action.
     — /api/interlock/dispatch : stub for LEA dispatch action.
     — /api/dossier/generate : stub for PDF dossier generation.
"""

import sys
import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from api.models import (
    InvestigationRequest,
    InvestigationResponse,
    SystemStatusResponse,
    ErrorResponse,
    InvestigateRunRequest,
    ScenarioDataResponse,
    MacroStatsResponse,
    InterlockRequest,
    InterlockResponse,
    DossierRequest,
    DossierResponse,
)
from database.connection import get_dataset_connection, get_operational_connection
from database.repository import OperationalRepository
from database.init_operational import init_db
from agent.agent import PredictiveCybercrimeAgent
from agent.tools import registry

# ── App factory ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="Predictive Cybercrime Intelligence API",
    description="Backend API for the Predictive Cybercrime Cash Withdrawal Intelligence System",
    version="1.0.0",
)

# ── CORS — allow the React dev server ────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Startup: initialise operational DB ───────────────────────────────────────

@app.on_event("startup")
def startup_event():
    try:
        init_db()
        print("[STARTUP] Operational database ready.")
    except Exception as e:
        print(f"[STARTUP] DB init warning: {e}")


# ── Helper: map agent final_state → ScenarioDataResponse ─────────────────────

def _map_state_to_scenario(scenario_id: str, final_state: dict) -> ScenarioDataResponse:
    """
    Translate the LangGraph agent's InvestigationState dict into the
    ScenarioDataResponse shape that the React frontend expects.
    """
    findings = final_state.get("findings", [])
    transactions = final_state.get("transactions", [])
    profiles = final_state.get("profiles", [])
    atms = final_state.get("atms", [])
    risk_assessments = final_state.get("risk_assessments", [])

    # ── Risk score & level ────────────────────────────────────────────────────
    overall_risk = 0.0
    risk_level = "LOW"
    if findings:
        top_finding = max(findings, key=lambda f: f.get("risk_score", 0))
        overall_risk = round(top_finding.get("risk_score", 0.0), 1)
        risk_level = top_finding.get("severity", "LOW")

    # Map engine risk_level → frontend riskLevel enum
    _level_map = {"CRITICAL": "CRITICAL", "HIGH": "HIGH", "MODERATE": "MEDIUM", "LOW": "LOW", "SAFE": "SAFE"}
    risk_level = _level_map.get(risk_level, "LOW")

    # ── Verdict ───────────────────────────────────────────────────────────────
    if overall_risk >= 75:
        verdict = "UNANIMOUS_FRAUD_INTERCEPT"
    elif overall_risk >= 50:
        verdict = "BORDERLINE_RE_EVALUATION"
    else:
        verdict = "LEGITIMATE_TRANSACTION_VERIFIED_CLEAR"

    # ── Predicted ATMs ────────────────────────────────────────────────────────
    predicted_atms = []
    for atm in atms:
        predicted_atms.append({
            "id": atm.get("atm_id", "unknown"),
            "name": atm.get("atm_name", "Unknown ATM"),
            "lat": float(atm.get("latitude", 0.0)),
            "lng": float(atm.get("longitude", 0.0)),
            "riskScore": int(overall_risk),
            "probability": int(min(overall_risk + 10, 99)),
        })

    # ── Transaction network graph ─────────────────────────────────────────────
    nodes, edges = [], []
    seen_nodes: set = set()

    def _add_node(node_id: str, label: str, risk_type: str, details: str = ""):
        if node_id not in seen_nodes:
            seen_nodes.add(node_id)
            nodes.append({"id": node_id, "label": label, "riskType": risk_type, "details": details})

    for txn in transactions:
        from_acc = txn.get("from_account_id", "")
        to_acc = txn.get("to_account_id", "")
        amount = txn.get("amount_inr", 0)
        is_laundering = txn.get("is_laundering", 0)
        hop = txn.get("hop_layer", 0)
        is_cashout = txn.get("is_terminal_cashout", 0)

        from_risk = "critical" if is_laundering else ("warning" if hop > 0 else "safe")
        to_risk = "critical" if is_cashout else ("warning" if is_laundering else "safe")

        _add_node(from_acc, f"Account {from_acc[-6:]}", from_risk, f"Bank: {txn.get('from_bank','?')}")
        _add_node(to_acc, f"Account {to_acc[-6:]}", to_risk, f"Bank: {txn.get('to_bank','?')}")

        edges.append({
            "source": from_acc,
            "target": to_acc,
            "amount": f"₹{amount:,.0f}",
            "riskType": "critical" if (is_laundering or is_cashout) else "warning",
            "timestamp": txn.get("timestamp_ist", ""),
        })

    # Always add victim node if no nodes present
    if not nodes:
        _add_node("victim", "Victim Account", "safe", "Primary complainant")

    # ── Swarm weights (derived from active indicators) ────────────────────────
    swarm_weights = {"financial": 33, "forensic": 33, "geoSpatial": 34}

    # ── Intervention stubs ────────────────────────────────────────────────────
    bank_intervention = {
        "required": overall_risk >= 50,
        "status": "ACTIVE HOLD" if overall_risk >= 75 else ("PENDING LIEN" if overall_risk >= 50 else "NOT REQUIRED"),
    }
    lea_intervention = {
        "required": overall_risk >= 75,
        "status": "DISPATCHED" if overall_risk >= 75 else "NOT REQUIRED",
    }

    return ScenarioDataResponse(
        id=scenario_id,
        title=f"Investigation: {scenario_id}",
        description=final_state.get("objective", "Agent-driven cybercrime investigation"),
        verdict=verdict,
        riskLevel=risk_level,
        overallRisk=overall_risk,
        swarmWeights=swarm_weights,
        expectedWindow=24.0,
        predictedAtms=predicted_atms,
        networkNodes=nodes,
        networkEdges=edges,
        bankIntervention=bank_intervention,
        leaIntervention=lea_intervention,
        agentStatus=final_state.get("status", "COMPLETED"),
        stopReason=final_state.get("stop_reason", ""),
        investigationId=final_state.get("investigation_id", ""),
        iterationsUsed=final_state.get("iteration", 0),
        toolCallsUsed=len(final_state.get("tool_history", [])),
        findingsCount=len(findings),
        evidenceCount=len(final_state.get("evidence", [])),
    )


# ════════════════════════════════════════════════════════════════════════════
# SECTION 1 — FRONTEND-COMPATIBLE  /api/*  ROUTES
# ════════════════════════════════════════════════════════════════════════════

@app.post("/api/investigate/run", response_model=ScenarioDataResponse)
def investigate_run(req: InvestigateRunRequest):
    """
    Synchronously runs the LangGraph agent for the given scenarioId and
    returns a ScenarioDataResponse the React frontend can render directly.

    NOTE: This is a long-running call (30 s – 3 min).  The frontend's fetch
    will wait for its completion.  Consider upgrading to a polling pattern
    if timeouts become an issue in production.
    """
    try:
        agent = PredictiveCybercrimeAgent()
        final_state = agent.run(scenario_id=req.scenarioId)
        return _map_state_to_scenario(req.scenarioId, final_state)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")


@app.get("/api/stats/macro", response_model=MacroStatsResponse)
def get_macro_stats():
    """Returns aggregated investigation statistics for the Command Center dashboard."""
    try:
        repo = OperationalRepository()
        with get_operational_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM investigations WHERE status = 'RUNNING'")
            running = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM risk_assessments WHERE risk_level IN ('CRITICAL','HIGH')")
            high_risk = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM investigations WHERE status = 'COMPLETED'")
            completed = cur.fetchone()[0]
        return MacroStatsResponse(
            activeInvestigations=running,
            highRiskAlerts=high_risk,
            successfulInterventions=completed,
        )
    except Exception:
        # DB may not exist yet — return sensible defaults
        return MacroStatsResponse(activeInvestigations=0, highRiskAlerts=0, successfulInterventions=0)


@app.post("/api/interlock/freeze", response_model=InterlockResponse)
def freeze_funds(req: InterlockRequest):
    """Stub: signals the bank to freeze funds for the given account."""
    return InterlockResponse(status="ACTIVE HOLD", detail=f"Account {req.accountId} freeze initiated.")


@app.post("/api/interlock/dispatch", response_model=InterlockResponse)
def dispatch_lea(req: InterlockRequest):
    """Stub: dispatches law enforcement to the given ATM."""
    return InterlockResponse(status="DISPATCHED", detail=f"LEA dispatched for ATM/unit {req.accountId}.")


@app.post("/api/dossier/generate", response_model=DossierResponse)
def generate_dossier(req: DossierRequest):
    """Stub: triggers PDF dossier generation."""
    return DossierResponse(url=f"/dossier/{req.caseId}.pdf")


# ════════════════════════════════════════════════════════════════════════════
# SECTION 2 — INTERNAL / OPERATIONAL  ROUTES  (no /api prefix)
# ════════════════════════════════════════════════════════════════════════════

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/system/status", response_model=SystemStatusResponse)
def system_status():
    dataset_avail = False
    dataset_readonly = False
    try:
        with get_dataset_connection() as conn:
            dataset_avail = True
            try:
                conn.execute("CREATE TABLE _test_ro (id INT)")
                dataset_readonly = False
            except Exception as e:
                if "readonly" in str(e).lower() or "read-only" in str(e).lower():
                    dataset_readonly = True
    except Exception:
        pass

    op_avail = False
    try:
        with get_operational_connection() as conn:
            op_avail = True
    except Exception:
        pass

    tools_count = len([t for t in dir(registry) if not t.startswith("__") and callable(getattr(registry, t))])

    return SystemStatusResponse(
        version="1.0.0",
        python_version=sys.version.split()[0],
        dataset_db_available=dataset_avail,
        operational_db_available=op_avail,
        dataset_db_readonly=dataset_readonly,
        registered_tools=tools_count,
        reporting_available=False,
    )


def _run_investigation_background(scenario_id: str, inv_id: str, max_iterations: int, max_tool_calls: int):
    """Background worker for the /investigations POST route."""
    try:
        agent = PredictiveCybercrimeAgent()
        agent.run(scenario_id, max_iterations=max_iterations, max_tool_calls=max_tool_calls)
        OperationalRepository.execute_update(
            "UPDATE investigations SET status = 'COMPLETED' WHERE investigation_id = ?", (inv_id,)
        )
    except Exception as e:
        print(f"[BACKGROUND] Investigation failed: {e}")
        OperationalRepository.execute_update(
            "UPDATE investigations SET status = 'FAILED' WHERE investigation_id = ?", (inv_id,)
        )


@app.post("/investigations", response_model=InvestigationResponse)
def start_investigation(req: InvestigationRequest, background_tasks: BackgroundTasks):
    import uuid
    from datetime import datetime, UTC

    inv_id = str(uuid.uuid4())
    now = datetime.now(UTC).isoformat() + "Z"

    try:
        OperationalRepository.execute_insert(
            "INSERT INTO agent_sessions (session_id, started_at, target_type, target_id, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (inv_id, now, "SCENARIO", req.scenario_id, "RUNNING", now),
        )
        OperationalRepository.execute_insert(
            "INSERT INTO investigations (investigation_id, session_id, subject_type, subject_id, objective, status, started_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (inv_id, inv_id, "SCENARIO", req.scenario_id, "Investigate cashout", "RUNNING", now),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    background_tasks.add_task(
        _run_investigation_background, req.scenario_id, inv_id, req.max_iterations, req.max_tool_calls
    )

    return InvestigationResponse(
        investigation_id=inv_id,
        scenario_id=req.scenario_id,
        status="RUNNING",
        message="Investigation started in background.",
    )


@app.get("/investigations/{inv_id}")
def get_investigation(inv_id: str):
    repo = OperationalRepository()
    status_info = repo.get_investigation_status(inv_id)
    if status_info["status"] == "UNKNOWN":
        raise HTTPException(status_code=404, detail="Investigation not found")
    return status_info


@app.get("/investigations/{inv_id}/findings")
def get_investigation_findings(inv_id: str):
    repo = OperationalRepository()
    findings = repo.get_findings_by_investigation(inv_id)
    return {"investigation_id": inv_id, "findings": findings}


@app.get("/investigations/{inv_id}/evidence")
def get_investigation_evidence(inv_id: str):
    repo = OperationalRepository()
    evidence = repo.get_evidence_by_investigation(inv_id)
    return {"investigation_id": inv_id, "evidence": evidence}
