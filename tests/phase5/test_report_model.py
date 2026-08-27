import pytest
from reporting.models import SecurityAssessmentReport, ReportMode, FindingModel, FindingLifecycleStatus

def test_report_model_creation():
    rep = SecurityAssessmentReport.create_empty("INV1", "SCEN1", ReportMode.SYNTHETIC_DEMO)
    assert rep.investigation_id == "INV1"
    assert rep.mode == ReportMode.SYNTHETIC_DEMO
    assert len(rep.findings) == 0

def test_finding_model_validation():
    with pytest.raises(ValueError, match="risk_score must be in"):
        FindingModel(
            finding_id="1", investigation_id="1", title="T", category="C", description="D",
            severity="HIGH", risk_score=150.0, confidence=1.0, status=FindingLifecycleStatus.OPEN,
            indicator_ids=[], evidence_ids=[], recommendations=[], created_at="N", updated_at="N"
        )
