import pytest
from evidence.models import EvidenceItem, EvidenceClassification
from evidence.validator import EvidenceValidator
from evaluation.engine import EvaluationEngine, EvaluationResult

def test_evidence_provenance_validation():
    # Inferred evidence without parent_evidence_id should fail validator
    e = EvidenceItem.create(
        evidence_id="E1",
        investigation_id="INV1",
        source_type="SCENARIO",
        source_id="S1",
        observed_field="status",
        observed_value="suspicious",
        description="Inferred status",
        confidence=0.9,
        classification=EvidenceClassification.INFERRED,
        parent_evidence_id=None
    )
    
    valid, errors = EvidenceValidator.validate(e)
    assert not valid
    assert any("MUST have a parent_evidence_id" in err for err in errors)

def test_evidence_provenance_success():
    # Inferred evidence with parent_evidence_id should pass
    e = EvidenceItem.create(
        evidence_id="E1",
        investigation_id="INV1",
        source_type="SCENARIO",
        source_id="S1",
        observed_field="status",
        observed_value="suspicious",
        description="Inferred status",
        confidence=0.9,
        classification=EvidenceClassification.INFERRED,
        parent_evidence_id="E_PARENT"
    )
    
    valid, errors = EvidenceValidator.validate(e)
    assert valid
    assert len(errors) == 0

def test_evaluation_engine_deterministic():
    # Test scoring mechanisms
    result = {
        "investigation_id": "INV1",
        "status": "COMPLETED",
        "evidence": [
            {
                "evidence_id": "E1",
                "classification": "OBSERVED",
                "confidence": 1.0
            }
        ],
        "findings": [
            {
                "finding_id": "F1",
                "evidence_ids": ["E1"]
            }
        ],
        "risk_assessments": [
            {
                "risk_score": 85.0
            }
        ],
        "tool_calls": 5
    }
    
    eval_res = EvaluationEngine.evaluate(result)
    assert eval_res.evidence_quality_score == 100.0
    assert eval_res.finding_consistency_score == 100.0
    assert eval_res.risk_consistency_score == 100.0
    assert eval_res.efficiency_score == 100.0

def test_evaluation_engine_missing_evidence():
    result = {
        "investigation_id": "INV1",
        "status": "COMPLETED",
        "evidence": [],
        "findings": [],
        "risk_assessments": [],
        "tool_calls": 5
    }
    
    eval_res = EvaluationEngine.evaluate(result)
    assert eval_res.evidence_quality_score == 0.0
    assert eval_res.evidence_completeness_score == 0.0
    assert len(eval_res.failures) > 0
    assert "Completed investigation has no evidence." in eval_res.failures
