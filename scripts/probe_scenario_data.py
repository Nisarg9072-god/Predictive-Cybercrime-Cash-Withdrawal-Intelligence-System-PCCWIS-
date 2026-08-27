import sqlite3
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

db_path = 'data/synthetic/CYBER_INTERCEPT_FULL_DATASET/cyber_intercept.db'

conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
conn.text_factory = lambda b: b.decode(errors='replace')
cur = conn.cursor()

# Test what queries on transactions work
print("=== TRANSACTION TABLE INVESTIGATION ===")

tests = [
    ("Count all", "SELECT count(*) FROM transactions"),
    ("Count is_laundering=1", "SELECT count(*) FROM transactions WHERE is_laundering = 1"),
    ("Count is_terminal_cashout=1", "SELECT count(*) FROM transactions WHERE is_terminal_cashout = 1"),
    ("Max hop_layer", "SELECT max(hop_layer) FROM transactions"),
    ("Distinct crime categories", "SELECT DISTINCT crime_category FROM transactions"),
    ("APK category count", "SELECT count(*) FROM transactions WHERE crime_category = 'APK/Malware Scam'"),
    ("Chain count", "SELECT count(DISTINCT chain_id) FROM transactions"),
    ("Sample chain IDs", "SELECT DISTINCT chain_id FROM transactions LIMIT 5"),
]

for desc, q in tests:
    try:
        cur.execute(q)
        r = cur.fetchall()
        print(f"  {desc}: {r}")
    except Exception as e:
        print(f"  {desc}: ERROR - {e}")

# Test fetching specific chains
print("\n=== CHAIN TRANSACTIONS (CHAIN_00001) ===")
try:
    cur.execute("SELECT txn_id, from_account_id, to_account_id, amount_inr, hop_layer, is_laundering, is_terminal_cashout FROM transactions WHERE chain_id = 'CHAIN_00001' ORDER BY hop_layer")
    rows = cur.fetchall()
    for r in rows:
        print(f"  hop={r[4]} from={r[1][:20]} to={r[2][:20]} amt={r[3]} launder={r[5]} cashout={r[6]}")
except Exception as e:
    print(f"  ERROR: {e}")

# Try profiles via SQL without any index
print("\n=== PROFILES (NO INDEX) ===")
try:
    # Use NOT INDEXED hint 
    cur.execute("SELECT profile_id, account_id, bank_name, is_mule, risk_score FROM profiles NOT INDEXED LIMIT 10")
    rows = cur.fetchall()
    print(f"  Got {len(rows)} rows")
    for r in rows:
        print(f"  {r}")
except Exception as e:
    print(f"  ERROR: {e}")

# Try fetching specific profile by known account_id
print("\n=== PROFILE BY ACCOUNT_ID ===")
test_accounts = ['ACC_AXIS_0000002_4570596497', 'ACC_UBIN_0000003_6611634494', 'ACC_PAYTM_0000005_2739747358']
for acc in test_accounts:
    try:
        cur.execute("SELECT profile_id, account_id, is_mule, mule_type, risk_score FROM profiles WHERE account_id = ?", (acc,))
        r = cur.fetchone()
        print(f"  {acc}: {r}")
    except Exception as e:
        print(f"  {acc}: ERROR - {e}")

conn.close()
