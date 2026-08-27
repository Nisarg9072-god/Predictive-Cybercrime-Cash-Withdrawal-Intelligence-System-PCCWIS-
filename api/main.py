import sys
import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from api.models import InvestigationRequest, InvestigationResponse, SystemStatusResponse, ErrorResponse
from database.connection import get_dataset_connection, get_operational_connection
from database.repository import OperationalRepository
from agent.agent import PredictiveCybercrimeAgent
from reporting.service import ReportService
from reporting.models import ReportMode
from agent.tools import registry

app = FastAPI(
    title="Predictive Cybercrime Intelligence API",
    description="Development API for the Predictive Cybercrime Cash Withdrawal Intelligence System",
    version="1.0.0"
)

def run_investigation_background(scenario_id: str, inv_id: str, max_iterations: int, max_tool_calls: int, is_synthetic: bool):
    """Background task to run the investigation."""
    try:
        if is_synthetic:
            # Synthetic flow: we don't use real DB or real agent state, just dummy it
            svc = ReportService()
            svc.create_report(
                investigation_id=inv_id,
                scenario_id=scenario_id,
                mode=ReportMode.SYNTHETIC_DEMO,
                agent_state=None,
                audit_events=[]
            )
            # Update investigation status to COMPLETED
            OperationalRepository.execute_update("UPDATE investigations SET status = 'COMPLETED' WHERE investigation_id = ?", (inv_id,))
            return
            
        agent = PredictiveCybercrimeAgent()
        state = agent.run(scenario_id, max_iterations=max_iterations, max_tool_calls=max_tool_calls)
        
        # Report is handled inside the agent or via service
        svc = ReportService()
        status_to_report = ReportMode.REAL
        if state.get("status") == "BLOCKED" or state.get("stop_reason") == "DATASET_CORRUPTED":
            status_to_report = ReportMode.REAL # it handles BLOCKED inside based on validation
            
        svc.create_report(
            investigation_id=inv_id,
            scenario_id=scenario_id,
            mode=status_to_report,
            agent_state=state,
            audit_events=[]
        )
    except Exception as e:
        print(f"Background investigation failed: {e}")
        OperationalRepository.execute_update("UPDATE investigations SET status = 'FAILED' WHERE investigation_id = ?", (inv_id,))

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
    except:
        pass
        
    op_avail = False
    try:
        with get_operational_connection() as conn:
            op_avail = True
    except:
        pass
        
    tools_count = len([t for t in dir(registry) if not t.startswith("__") and callable(getattr(registry, t))])
    
    return SystemStatusResponse(
        version="1.0.0",
        python_version=sys.version.split()[0],
        dataset_db_available=dataset_avail,
        operational_db_available=op_avail,
        dataset_db_readonly=dataset_readonly,
        registered_tools=tools_count,
        reporting_available=True
    )

@app.post("/investigations", response_model=InvestigationResponse)
def start_investigation(req: InvestigationRequest, background_tasks: BackgroundTasks):
    import uuid
    from datetime import datetime, UTC
    
    inv_id = str(uuid.uuid4())
    now = datetime.now(UTC).isoformat() + "Z"
    
    # Initialize basic state in DB
    try:
        OperationalRepository.execute_insert(
            "INSERT INTO agent_sessions (session_id, started_at, target_type, target_id, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (inv_id, now, "SCENARIO", req.scenario_id, "RUNNING", now)
        )
        OperationalRepository.execute_insert(
            "INSERT INTO investigations (investigation_id, session_id, subject_type, subject_id, objective, status, started_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (inv_id, inv_id, "SCENARIO", req.scenario_id, "Investigate cashout", "RUNNING", now)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
        
    background_tasks.add_task(run_investigation_background, req.scenario_id, inv_id, req.max_iterations, req.max_tool_calls, req.is_synthetic)
    
    return InvestigationResponse(
        investigation_id=inv_id,
        scenario_id=req.scenario_id,
        status="RUNNING",
        message="Investigation started in background."
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

@app.get("/investigations/{inv_id}/report")
def get_investigation_report(inv_id: str):
    repo = OperationalRepository()
    reports = repo.list_reports_by_investigation(inv_id)
    if not reports:
        raise HTTPException(status_code=404, detail="No report generated yet.")
    
    rep = reports[0]
    return {
        "report_id": rep.report_id,
        "investigation_id": rep.investigation_id,
        "mode": rep.mode,
        "pdf_path": rep.pdf_path,
        "sha256": rep.sha256,
        "generated_at": rep.generated_at
    }
