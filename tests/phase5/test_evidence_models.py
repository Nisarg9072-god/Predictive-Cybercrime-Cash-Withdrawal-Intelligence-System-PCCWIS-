import pytest
from evidence.models import EvidenceItem, EvidenceClassification
from evidence.deduplicator import EvidenceDeduplicator
from evidence.validator import EvidenceValidator

def test_evidence_hashing():
    e1 = EvidenceItem.create("eid1", "inv1", "SOURCE", "sid1", "field1", 100, "desc", 0.9, EvidenceClassification.OBSERVED)
    e2 = EvidenceItem.create("eid2", "inv1", "SOURCE", "sid1", "field1", 100, "desc", 0.9, EvidenceClassification.OBSERVED)
    
    # Hash should be identical for same content, regardless of evidence_id
    assert e1.hash == e2.hash

    # Different value -> different hash
    e3 = EvidenceItem.create("eid3", "inv1", "SOURCE", "sid1", "field1", 101, "desc", 0.9, EvidenceClassification.OBSERVED)
    assert e1.hash != e3.hash

def test_evidence_deduplication():
    e1 = EvidenceItem.create("eid1", "inv1", "SRC", "1", "f", "v", "d", 0.9, EvidenceClassification.OBSERVED)
    e2 = EvidenceItem.create("eid2", "inv1", "SRC", "1", "f", "v", "d", 0.9, EvidenceClassification.OBSERVED)
    
    unique, reuse = EvidenceDeduplicator.deduplicate([e2], [e1])
    assert len(unique) == 0
    assert reuse["eid2"] == "eid1"

def test_evidence_validator():
    e = EvidenceItem.create("eid1", "inv1", "SRC", "1", "f", "v", "direct observation", 0.9, EvidenceClassification.INFERRED)
    
    ok, errs = EvidenceValidator.validate(e)
    assert not ok
    assert any("claim to be directly observed" in err for err in errs)
