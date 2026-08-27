import pytest
from remediation.engine import RemediationEngine

def test_remediation_mapping():
    recs = RemediationEngine.get_recommendations("TRANSACTION_LAUNDERING_PATTERN")
    assert len(recs) > 0
    assert recs[0]["label"] == "RECOMMENDATION"
    assert "REC-LAU-" in recs[0]["code"]

def test_remediation_fallback():
    recs = RemediationEngine.get_recommendations("UNKNOWN_PATTERN")
    assert len(recs) == 1
    assert recs[0]["code"] == "REC-GEN-001"
