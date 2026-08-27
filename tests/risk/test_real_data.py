"""
LEVEL C — Real Data Validation

Attempts to query the master database and run SCENARIO_001.
If corruption blocks it, marks tests as BLOCKED (xfail) rather than PASS.
"""
import pytest
import sqlite3
import os

DATASET_PATH = "data/synthetic/CYBER_INTERCEPT_FULL_DATASET/cyber_intercept.db"


def _can_read_transactions():
    """Returns True if the transactions table can be read."""
    try:
        conn = sqlite3.connect(f"file:{DATASET_PATH}?mode=ro", uri=True)
        conn.text_factory = lambda b: b.decode(errors="replace")
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM transactions WHERE is_terminal_cashout = 1")
        count = cur.fetchone()[0]
        conn.close()
        return count > 0
    except Exception:
        return False


def _can_read_profiles():
    """Returns True only if actual profile row column data can be fetched (not just count)."""
    try:
        conn = sqlite3.connect(f"file:{DATASET_PATH}?mode=ro", uri=True)
        conn.text_factory = lambda b: b.decode(errors="replace")
        cur = conn.cursor()
        # SELECT * to force B-tree page traversal — count(*) may succeed even on corrupted tables
        cur.execute(
            "SELECT profile_id, account_id, is_mule FROM profiles LIMIT 1"
        )
        row = cur.fetchone()
        conn.close()
        return row is not None
    except Exception:
        return False


def _can_read_scenarios():
    """Returns True if SCENARIO_001 is readable."""
    try:
        conn = sqlite3.connect(f"file:{DATASET_PATH}?mode=ro", uri=True)
        conn.text_factory = lambda b: b.decode(errors="replace")
        cur = conn.cursor()
        cur.execute(
            "SELECT scenario_id FROM scenarios WHERE scenario_id = 'SCENARIO_001'"
        )
        row = cur.fetchone()
        conn.close()
        return row is not None
    except Exception:
        return False


class TestMasterDBHealth:
    def test_db_file_exists(self):
        assert os.path.exists(DATASET_PATH), f"Master DB missing at {DATASET_PATH}"

    def test_db_size_plausible(self):
        size_gb = os.path.getsize(DATASET_PATH) / (1024 ** 3)
        assert size_gb > 1.0, "Master DB suspiciously small"

    def test_scenarios_table_readable(self):
        """SCENARIO_001 metadata should be accessible."""
        assert _can_read_scenarios(), "SCENARIO_001 not accessible — MASTER_DB_HEALTH: FAIL"

    @pytest.mark.xfail(
        not _can_read_profiles(),
        reason="profiles table is inaccessible due to B-tree corruption — MASTER_DB_HEALTH: FAIL (BLOCKED)",
        strict=False
    )
    def test_profiles_table_readable(self):
        assert _can_read_profiles(), "profiles table BLOCKED by corruption"

    def test_transactions_terminal_cashout_readable(self):
        """Terminal cashout transactions should be countable."""
        conn = sqlite3.connect(f"file:{DATASET_PATH}?mode=ro", uri=True)
        conn.text_factory = lambda b: b.decode(errors="replace")
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM transactions WHERE is_terminal_cashout = 1")
        count = cur.fetchone()[0]
        conn.close()
        assert count > 0, "Expected terminal cashout transactions"

    def test_scenario_001_data_json_parseable(self):
        """data_json for SCENARIO_001 should be valid JSON — currently BLOCKED."""
        import json
        conn = sqlite3.connect(f"file:{DATASET_PATH}?mode=ro", uri=True)
        conn.text_factory = lambda b: b.decode(errors="replace")
        cur = conn.cursor()
        cur.execute("SELECT data_json FROM scenarios WHERE scenario_id = 'SCENARIO_001'")
        row = cur.fetchone()
        conn.close()
        dj = row[0] if row else None
        try:
            json.loads(dj)
            parsed = True
        except Exception:
            parsed = False
        # Mark explicitly: this is currently BLOCKED
        if not parsed:
            pytest.xfail("data_json for SCENARIO_001 contains binary garbage — REAL_DATA_E2E: BLOCKED")


class TestRealScenarioE2E:
    """
    Attempts to run a full investigation against SCENARIO_001.
    If blocked by DB corruption, marks as xfail with explicit reason.
    """

    @pytest.mark.xfail(
        not (_can_read_scenarios() and _can_read_profiles()),
        reason="Master DB corruption prevents E2E — REAL_SCENARIO_E2E: BLOCKED",
        strict=False
    )
    def test_scenario_001_investigation_produces_findings(self):
        """Full E2E: run SCENARIO_001, expect at least one finding."""
        from agent.agent import PredictiveCybercrimeAgent
        agent = PredictiveCybercrimeAgent()
        final_state = agent.run("SCENARIO_001", max_iterations=10, max_tool_calls=15)
        assert final_state is not None, "Agent returned no state"
        findings = final_state.get("findings", [])
        assert len(findings) > 0, "No findings generated — investigation may be blocked"

    @pytest.mark.xfail(
        not _can_read_scenarios(),
        reason="scenarios table BLOCKED — REAL_SCENARIO_E2E: BLOCKED",
        strict=False
    )
    def test_scenario_001_scenario_loadable(self):
        """Scenario metadata must load from the database."""
        from database.repository import DatasetRepository
        scenario = DatasetRepository.get_scenario("SCENARIO_001")
        assert scenario is not None, "SCENARIO_001 not found in scenarios table"
        assert scenario.scenario_id == "SCENARIO_001"
