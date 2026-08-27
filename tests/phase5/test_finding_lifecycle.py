import pytest
import uuid
from database.repository import OperationalRepository
from reporting.models import FindingTransition, FindingLifecycleStatus
from datetime import datetime, UTC

def test_finding_lifecycle_logging():
    repo = OperationalRepository()
    inv_id = f"TEST_INV_{uuid.uuid4().hex[:8]}"
    fid = f"F_{uuid.uuid4().hex[:8]}"
    
    t = FindingTransition(
        transition_id=str(uuid.uuid4()),
        finding_id=fid,
        investigation_id=inv_id,
        from_status=FindingLifecycleStatus.OPEN,
        to_status=FindingLifecycleStatus.UNDER_REVIEW,
        reason="Analyst started review",
        transitioned_at=datetime.now(UTC).isoformat(),
        transitioned_by="system"
    )
    
    repo.log_finding_transition(t)
    # verify it doesn't crash, we haven't exposed `get_finding_transitions` to repo but query exists.
