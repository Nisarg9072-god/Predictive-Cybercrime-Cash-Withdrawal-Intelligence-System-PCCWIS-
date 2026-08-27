import pytest
import os
import uuid
from reporting.service import ReportService
from reporting.models import ReportMode

def test_synthetic_e2e_pipeline():
    svc = ReportService(output_dir="reports")
    inv_id = f"TEST_INV_{uuid.uuid4().hex[:8]}"
    
    res = svc.create_report(
        investigation_id=inv_id,
        scenario_id="SYNTHETIC_SCENARIO",
        mode=ReportMode.SYNTHETIC_DEMO,
        agent_state=None,
        audit_events=[]
    )
    
    assert res["report_id"] is not None
    assert res["mode"] == "SYNTHETIC_DEMO"
    assert "pdf_path" in res
    assert os.path.exists(res["pdf_path"])
    
    # Verify hash
    verify_res = svc.verify_report(res["report_id"])
    assert verify_res["verified"] is True
    assert verify_res["is_valid_pdf"] is True
    
    # Check that report size is > 1KB (meaning it has content)
    size = os.path.getsize(res["pdf_path"])
    assert size > 1024
