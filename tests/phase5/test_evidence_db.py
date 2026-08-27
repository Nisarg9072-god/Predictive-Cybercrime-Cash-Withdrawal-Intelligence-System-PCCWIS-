import pytest
import uuid
from database.repository import OperationalRepository
from evidence.models import EvidenceItem, EvidenceClassification

@pytest.fixture(autouse=True)
def setup_teardown():
    yield

def test_evidence_db_persistence():
    repo = OperationalRepository()
    inv_id = f"TEST_INV_{uuid.uuid4().hex[:8]}"
    
    e1 = EvidenceItem.create("eid1", inv_id, "T", "1", "f", "v", "d", 0.9, EvidenceClassification.OBSERVED)
    repo.save_evidence(e1)
    
    # Try duplicate hash save
    repo.save_evidence(e1)
    
    items = repo.get_evidence_by_investigation(inv_id)
    assert len(items) == 1
    assert items[0]["evidence_id"] == "eid1"
    assert items[0]["hash"] == e1.hash
