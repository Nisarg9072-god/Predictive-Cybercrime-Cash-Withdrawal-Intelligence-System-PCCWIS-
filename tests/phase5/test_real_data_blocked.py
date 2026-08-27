import pytest
import uuid
from reporting.service import ReportService
from reporting.models import ReportMode
from reporting.models import ValidationStatus

def test_real_data_blocked():
    svc = ReportService(output_dir="reports")
    inv_id = f"TEST_INV_{uuid.uuid4().hex[:8]}"
    
    res = svc.create_report(
        investigation_id=inv_id,
        scenario_id="SCENARIO_001",
        mode=ReportMode.REAL,
        agent_state=None,
        audit_events=[]
    )
    
    assert res["mode"] == "REAL"
    
    # Fetch report from DB
    rep_record = svc.get_report(res["report_id"])
    
    # Rebuild report manually to check internal validation status
    # since we want to assert that the REAL pipeline returns BLOCKED status for e2e
    from reporting.builder import ReportBuilder
    report = ReportBuilder.build(inv_id, "SCENARIO_001", ReportMode.REAL, None, [])
    
    assert report.validation_status["master_db"] == ValidationStatus.FAIL
    assert report.validation_status["real_e2e"] == ValidationStatus.BLOCKED
    assert "inaccessible" in report.executive_summary.lower()
