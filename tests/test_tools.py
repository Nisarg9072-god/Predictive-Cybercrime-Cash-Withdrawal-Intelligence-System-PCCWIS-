import pytest
from security.sanitizer import Sanitizer
from agent.tools import registry

def test_sanitizer():
    assert Sanitizer.mask_account_number("123456789") == "****6789"
    assert Sanitizer.mask_phone_number("+919876543210") == "+91****3210"
    assert Sanitizer.mask_pan("ABCDE1234F") == "AB******4F"

def test_transaction_search_pagination():
    # Attempt a small query that relies on limit.
    # Note: depends on real DB data existing. We will just check it doesn't crash
    res = registry.search_transactions(from_account="SOME_RANDOM_ACCOUNT_NOT_EXIST")
    assert res.success is True
    assert len(res.data) == 0

def test_get_scenario_raw():
    # If the DB has any data, we can test getting a raw scenario. If not, it shouldn't crash.
    res = registry.get_scenario_raw("SCENARIO_UNKNOWN")
    assert res.success is False
    assert "error" in res.model_dump()
