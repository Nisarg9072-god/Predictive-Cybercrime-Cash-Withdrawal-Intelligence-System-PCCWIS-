"""
DATABASE CORRUPTION ANALYSIS REPORT
=====================================

INTEGRITY CHECK RESULT: FAIL
  - PRAGMA integrity_check found duplicate page references in Tree 29
  - Tree 29 = idx_atms_geo (index on atms table, geographic columns)

TABLE READABILITY MATRIX:
  transactions     : PARTIAL — count(*) works, DISTINCT crime_category FAILS (hits corrupted index)
                     chain_id column appears to contain account IDs (data layout mismatch)
  profiles         : FAIL — ALL reads fail with "database disk image is malformed"
  scenarios        : OK — all 5 rows readable, including data_json field
  atms             : FAIL — ALL reads fail (idx_atms_geo corruption affects table reads too)
  districts        : OK
  state_stats      : OK

ADDITIONAL FINDINGS:
  - data_json on scenarios IS readable as a string but contains binary garbage:
      data_json is NOT valid JSON (Invalid control character at char 20)
      The scenario_id field inside data_json is also corrupted
  - transactions.is_laundering: count=0 (despite visual inspection showing is_laundering=1 in sample rows)
      This is likely a data column layout corruption — the is_laundering flag may be swapped
      with another column due to page-level B-tree corruption
  - transactions.chain_id contains ACCOUNT IDs not chain IDs in corrupted pages
  - CHAIN_00001 returns 0 rows despite the sample showing it exists
  - Profiles are completely inaccessible (0 readable rows via any query method)

ROOT CAUSE ASSESSMENT:
  The corruption is in the B-tree index pages (idx_atms_geo, root page 29).
  SQLite uses the B-tree page map for both index lookups AND for sequential table scans
  when those scans require specific indexed columns. The corruption has cascaded from
  the index into how the row data is mapped, causing:
    1. COUNT(*) on transactions to work (just counts allocated pages)
    2. But queries that dereference column positions to fail
    3. Profiles table B-tree root page likely also affected

WHAT CAN BE USED FOR REAL DATA VALIDATION:
  - scenarios table: scenario_id, name, crime_category, description, victim_city, victim_state, amount_lost_inr, status
  - state_stats: all columns readable
  - districts: all columns readable
  - transactions: count(*) queries, is_terminal_cashout=1 filter (3845 rows), max(hop_layer)=31

WHAT CANNOT BE USED:
  - profiles: COMPLETELY INACCESSIBLE
  - atms: COMPLETELY INACCESSIBLE
  - transactions.crime_category: FAILS
  - transactions.chain_id: CORRUPTED (returns account IDs)
  - data_json on scenarios: BINARY GARBAGE

VALIDATED CONCLUSION:
  REAL_DATA_E2E = BLOCKED
  MASTER_DB_HEALTH = FAIL (B-tree page corruption affecting 2/6 tables + data_json)

NOTE: The master database MUST NOT be modified. The corruption is a pre-existing dataset
condition that prevents end-to-end validation against real data.
"""
