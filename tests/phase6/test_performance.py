import pytest
import time
from database.repository import DatasetRepository
from database.queries import GET_NEARBY_ATMS

@pytest.mark.performance
def test_query_pagination():
    start = time.time()
    res1 = DatasetRepository.search_transactions(limit=10, offset=0)
    res2 = DatasetRepository.search_transactions(limit=10, offset=10)
    end = time.time()
    
    # Just asserting it executes without error. Since we are using an empty test DB
    # or the corrupted DB (where transactions still works), it should return fast.
    assert end - start < 1.0 # Should be very fast
    # It shouldn't crash
