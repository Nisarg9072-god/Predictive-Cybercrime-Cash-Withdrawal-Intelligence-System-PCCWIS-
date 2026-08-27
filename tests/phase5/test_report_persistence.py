import pytest
import uuid
from database.repository import OperationalRepository
from reporting.models import ReportRecord, ReportMode
from datetime import datetime, UTC

def test_report_persistence():
    repo = OperationalRepository()
    inv_id = f"TEST_INV_{uuid.uuid4().hex[:8]}"
    rid = f"REP_{uuid.uuid4().hex[:8]}"
    
    r = ReportRecord(
        report_id=rid,
        investigation_id=inv_id,
        scenario_id="SCEN1",
        mode=ReportMode.SYNTHETIC_DEMO.value,
        pdf_path="reports/dummy.pdf",
        sha256="abc",
        generated_at=datetime.now(UTC).isoformat()
    )
    
    repo.save_report(r)
    
    fetched = repo.get_report_by_id(rid)
    assert fetched is not None
    assert fetched.report_id == rid
    assert fetched.sha256 == "abc"
    
    reports = repo.list_reports_by_investigation(inv_id)
    assert len(reports) == 1
    assert reports[0].report_id == rid
