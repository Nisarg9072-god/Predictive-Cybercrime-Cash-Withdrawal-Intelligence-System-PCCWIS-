import pytest
from reporting.explainability import ExplainabilityService
from evidence.models import EvidenceItem, EvidenceClassification

def test_deterministic_explainability():
    e = EvidenceItem.create("e1", "i1", "T", "1", "f", "v", "d", 0.9, EvidenceClassification.OBSERVED)
    
    exp = ExplainabilityService.explain_finding(
        finding_id="F1", title="Test Finding", category="CAT", severity="HIGH",
        risk_score=85.0, confidence=0.9, status="OPEN",
        indicators=[{"name": "IND1", "description": "Triggered IND1"}],
        evidence_items=[e]
    )
    
    assert exp["risk"] == "85/100"
    assert "Triggered IND1" in exp["why"][0]
    assert "1 item(s) collected" in exp["prose"]
    assert exp["source"] == "DETERMINISTIC"
