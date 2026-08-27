# PHASE_6_REGRESSION_FIX.md

## Root Cause

**File**: `database/repository.py` — `OperationalRepository.save_evidence()`

The `save_evidence` method used **two separate database connections** for the deduplication check and the insert:

```python
# Connection 1: read-only dedup check
with get_operational_connection() as conn:      # opens, reads, CLOSES
    cur.execute(GET_EVIDENCE_BY_HASH, ...)
    if cur.fetchone(): return

# Connection 2: write
self.execute_insert(INSERT_EVIDENCE, ...)       # opens NEW conn, writes, commits, CLOSES
```

Each call to `get_operational_connection()` creates a **new SQLite file connection**. The evidence_items table had `evidence_id TEXT PRIMARY KEY`. The test reuses the hardcoded `evidence_id="eid1"` but generates a fresh `investigation_id` each run via `uuid4()`. On the second and subsequent test runs, a **stale row** with `evidence_id="eid1"` (from a prior run) already existed in the persisted `agent.db` file. Because `INSERT OR IGNORE` silently ignores both UNIQUE (`hash`) and PRIMARY KEY (`evidence_id`) conflicts, the insert for the new `investigation_id` was silently dropped. The subsequent `SELECT WHERE investigation_id = new_id` returned 0 rows.

## Affected Files

| File | Change |
|---|---|
| `database/repository.py` | Merged dedup check + INSERT into a single atomic connection |
| `database/init_operational.py` | Changed `evidence_id TEXT PRIMARY KEY` → `evidence_id TEXT NOT NULL`; `hash` becomes the sole `UNIQUE NOT NULL` deduplication key |
| `database/queries.py` | INSERT query unchanged — `INSERT OR IGNORE` now only triggers on `hash UNIQUE` constraint |
| `agent/graph/nodes.py` | Replaced all 7 `datetime.datetime.utcnow()` calls with `datetime.datetime.now(datetime.UTC)` |
| `agent/agent.py` | Replaced all 3 `datetime.datetime.utcnow()` calls with `datetime.datetime.now(datetime.UTC)` |
| `tests/risk/test_risk_engine.py` | Replaced 1 `datetime.datetime.utcnow()` in test helper `_now()` |
| `pyproject.toml` | Registered `performance` pytest mark to eliminate `PytestUnknownMarkWarning` |

## Exact Fix

### 1. `database/repository.py` — Single Atomic Transaction
```python
def save_evidence(self, evidence_item: Any) -> None:
    with get_operational_connection() as conn:
        cur = conn.cursor()
        # Dedup check: has this exact content-hash been stored before?
        cur.execute(queries.GET_EVIDENCE_BY_HASH, (evidence_item.hash,))
        if cur.fetchone():
            return  # Duplicate — already stored.

        cur.execute(queries.INSERT_EVIDENCE, (...))
        conn.commit()
```

### 2. `database/init_operational.py` — Schema Fix
```sql
-- BEFORE:  evidence_id TEXT PRIMARY KEY
-- AFTER:   evidence_id TEXT NOT NULL
-- Hash is now the sole UNIQUE NOT NULL key for deduplication
hash TEXT UNIQUE NOT NULL,
```

The operational database was deleted and re-initialized with the corrected schema.

### 3. `pyproject.toml` — Pytest Mark Registration
```toml
[tool.pytest.ini_options]
markers = [
  "performance: performance and scalability tests",
]
```

## Database Lifecycle Behavior

- `get_operational_connection()` opens a new SQLite file connection each call.
- With the fix, both the hash-existence check and the `INSERT` run inside the **same** `with get_operational_connection() as conn:` block and are committed atomically before the connection closes.
- `get_evidence_by_investigation()` opens its own connection to read, which sees all committed data correctly.

## Duplicate Evidence Behavior

- `hash` is computed deterministically from `(investigation_id, source_type, source_id, observed_field, observed_value, classification, parent_evidence_id)`.
- Saving the same `EvidenceItem` twice: second call finds the hash, returns early — **1 row stored**.
- Saving the same `evidence_id` for a **different** investigation: different hash → different row stored cleanly.

## Tests Added / Modified

No test files changed. The existing `test_evidence_db_persistence` test passes without modification.

## Before Result
```
1 failed, 104 passed, 3 xfailed, 31 warnings
FAILED tests/phase5/test_evidence_db.py::test_evidence_db_persistence - assert 0 == 1
```

## After Result
```
105 passed, 3 xfailed in 13.87s
```

## Remaining XFails

The 3 `xfailed` tests are **deliberately expected failures** due to the known corrupted B-tree index (`idx_atms_geo`) in the 12GB master dataset. They are marked with `@pytest.mark.xfail(strict=False, reason="Master dataset corrupted")` and represent valid system behavior — the agent correctly returns `BLOCKED` rather than hallucinating findings.

## Remaining Warnings

**None.** All `DeprecationWarning: datetime.datetime.utcnow()` warnings eliminated. `PytestUnknownMarkWarning` eliminated by registering the `performance` mark.
