"""
LEVEL B — Operational Database Tests

Tests schema creation, insert, retrieval, and risk history persistence.
Uses a temporary in-memory SQLite database to avoid touching the production operational DB.
"""
import pytest
import sqlite3
import uuid
import datetime
import json


@pytest.fixture
def tmp_op_db():
    """In-memory operational DB with full schema."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS agent_sessions (
            session_id TEXT PRIMARY KEY,
            started_at TEXT, completed_at TEXT,
            target_type TEXT, target_id TEXT,
            status TEXT, iteration_count INTEGER DEFAULT 0,
            tool_call_count INTEGER DEFAULT 0, error TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS investigations (
            investigation_id TEXT PRIMARY KEY,
            session_id TEXT, subject_type TEXT, subject_id TEXT,
            objective TEXT, status TEXT, started_at TEXT, completed_at TEXT
        );
        CREATE TABLE IF NOT EXISTS findings (
            finding_id TEXT PRIMARY KEY, investigation_id TEXT,
            title TEXT, category TEXT, severity TEXT, confidence REAL,
            description TEXT, evidence_summary TEXT, remediation TEXT,
            status TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS audit_events (
            event_id TEXT PRIMARY KEY, session_id TEXT,
            event_type TEXT, component TEXT, status TEXT,
            metadata TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS risk_assessments (
            risk_assessment_id TEXT PRIMARY KEY,
            investigation_id TEXT, iteration INTEGER,
            risk_score REAL, risk_level TEXT, confidence REAL,
            indicator_ids TEXT, evidence_ids TEXT, created_at TEXT
        );
    """)
    conn.commit()
    yield conn
    conn.close()


def _now():
    return datetime.datetime.now(datetime.UTC).isoformat() + "Z"


class TestOperationalDBSchema:
    def test_risk_assessments_table_exists(self, tmp_op_db):
        cur = tmp_op_db.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='risk_assessments'")
        assert cur.fetchone() is not None

    def test_risk_assessments_columns(self, tmp_op_db):
        cur = tmp_op_db.cursor()
        cur.execute("PRAGMA table_info(risk_assessments)")
        cols = {row[1] for row in cur.fetchall()}
        expected = {
            "risk_assessment_id", "investigation_id", "iteration",
            "risk_score", "risk_level", "confidence",
            "indicator_ids", "evidence_ids", "created_at"
        }
        assert expected <= cols

    def test_findings_table_exists(self, tmp_op_db):
        cur = tmp_op_db.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='findings'")
        assert cur.fetchone() is not None


class TestRiskAssessmentPersistence:
    def _insert(self, conn, investigation_id, iteration, score, level, confidence, indicators, evidence):
        ra_id = str(uuid.uuid4())
        now = _now()
        conn.execute(
            "INSERT INTO risk_assessments VALUES (?,?,?,?,?,?,?,?,?)",
            (ra_id, investigation_id, iteration, score, level, confidence,
             ",".join(indicators), ",".join(evidence), now)
        )
        conn.commit()
        return ra_id

    def test_insert_risk_assessment(self, tmp_op_db):
        ra_id = self._insert(
            tmp_op_db, "INV-001", 1, 65.0, "HIGH", 0.75,
            ["IND_LAUNDERING_FLAG", "IND_TERMINAL_CASHOUT"], ["E1"]
        )
        cur = tmp_op_db.cursor()
        cur.execute("SELECT * FROM risk_assessments WHERE risk_assessment_id = ?", (ra_id,))
        row = cur.fetchone()
        assert row is not None
        assert row["risk_score"] == 65.0
        assert row["risk_level"] == "HIGH"
        assert row["confidence"] == 0.75

    def test_risk_history_multiple_iterations(self, tmp_op_db):
        inv_id = "INV-HIST-001"
        self._insert(tmp_op_db, inv_id, 1, 20.0, "LOW", 0.10, [], [])
        self._insert(tmp_op_db, inv_id, 2, 50.0, "HIGH", 0.40, ["IND_LAUNDERING_FLAG"], ["E1"])
        self._insert(tmp_op_db, inv_id, 3, 75.0, "CRITICAL", 0.80, ["IND_LAUNDERING_FLAG", "IND_TERMINAL_CASHOUT"], ["E1", "E2"])

        cur = tmp_op_db.cursor()
        cur.execute("SELECT * FROM risk_assessments WHERE investigation_id = ? ORDER BY iteration", (inv_id,))
        rows = cur.fetchall()
        assert len(rows) == 3
        assert rows[0]["risk_score"] == 20.0
        assert rows[1]["risk_score"] == 50.0
        assert rows[2]["risk_score"] == 75.0

    def test_risk_score_increases_with_evidence(self, tmp_op_db):
        inv_id = "INV-PROG-001"
        self._insert(tmp_op_db, inv_id, 1, 0.0, "LOW", 0.0, [], [])
        self._insert(tmp_op_db, inv_id, 2, 30.0, "MODERATE", 0.25, ["IND_LAUNDERING_FLAG"], ["E1"])
        self._insert(tmp_op_db, inv_id, 3, 75.0, "CRITICAL", 0.80, ["IND_LAUNDERING_FLAG", "IND_TERMINAL_CASHOUT", "IND_MULTI_HOP_CHAIN"], ["E1", "E2"])

        cur = tmp_op_db.cursor()
        cur.execute("SELECT risk_score FROM risk_assessments WHERE investigation_id = ? ORDER BY iteration", (inv_id,))
        scores = [row[0] for row in cur.fetchall()]
        assert scores == sorted(scores)  # monotonically increasing


class TestFindingPersistence:
    def test_insert_finding(self, tmp_op_db):
        now = _now()
        fid = str(uuid.uuid4())
        tmp_op_db.execute(
            "INSERT INTO findings VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (fid, "INV-001", "Evidence suggests multi-hop pattern",
             "MULTI_HOP_TRANSFER_PATTERN", "HIGH", 0.80,
             "Why:\n- 5 hop chain", "E1,E2", "Manual review", "POTENTIAL_PATTERN", now)
        )
        tmp_op_db.commit()

        cur = tmp_op_db.cursor()
        cur.execute("SELECT * FROM findings WHERE finding_id = ?", (fid,))
        row = cur.fetchone()
        assert row is not None
        assert row["category"] == "MULTI_HOP_TRANSFER_PATTERN"
        assert row["severity"] == "HIGH"

    def test_duplicate_finding_ids_rejected(self, tmp_op_db):
        now = _now()
        fid = str(uuid.uuid4())
        tmp_op_db.execute(
            "INSERT INTO findings VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (fid, "INV-001", "Test", "MULE_ACCOUNT_RISK", "MODERATE", 0.50,
             "Why", "E1", "Manual review", "POTENTIAL_PATTERN", now)
        )
        tmp_op_db.commit()
        with pytest.raises(Exception):
            tmp_op_db.execute(
                "INSERT INTO findings VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (fid, "INV-001", "Duplicate", "MULE_ACCOUNT_RISK", "MODERATE", 0.50,
                 "Why", "E1", "Manual review", "POTENTIAL_PATTERN", now)
            )
            tmp_op_db.commit()


class TestAuditPersistence:
    def test_insert_audit_event(self, tmp_op_db):
        now = _now()
        eid = str(uuid.uuid4())
        tmp_op_db.execute(
            "INSERT INTO audit_events VALUES (?,?,?,?,?,?,?)",
            (eid, "SES-001", "TOOL_EXECUTED", "NODE", "SUCCESS",
             json.dumps({"tool": "get_scenario_raw"}), now)
        )
        tmp_op_db.commit()

        cur = tmp_op_db.cursor()
        cur.execute("SELECT * FROM audit_events WHERE event_id = ?", (eid,))
        row = cur.fetchone()
        assert row is not None
        meta = json.loads(row["metadata"])
        assert meta["tool"] == "get_scenario_raw"
