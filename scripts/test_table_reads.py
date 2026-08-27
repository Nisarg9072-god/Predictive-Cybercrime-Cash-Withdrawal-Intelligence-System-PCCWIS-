import sqlite3
import os

db_path = 'data/synthetic/CYBER_INTERCEPT_FULL_DATASET/cyber_intercept.db'

# The corruption is in Tree 29 = idx_atms_geo (index, not a table).
# Check which tables can be fully read without the index
try:
    conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
    conn.text_factory = lambda b: b.decode(errors='replace')
    cur = conn.cursor()
    
    readable = {}
    
    # Try profiles
    try:
        cur.execute("SELECT profile_id, account_id, holder_name, bank_name, kyc_status, account_age_days, risk_score, is_mule, mule_type, last_known_city, last_known_state, withdrawal_velocity_per_day FROM profiles LIMIT 3")
        rows = cur.fetchall()
        readable['profiles'] = f"OK - {len(rows)} sample rows"
    except Exception as e:
        readable['profiles'] = f"PARTIAL/FAIL: {e}"
        # Try without LIMIT to diagnose
        try:
            cur.execute("SELECT count(*) FROM profiles WHERE is_mule = 1")
            c = cur.fetchone()[0]
            readable['profiles_mule_count'] = f"OK - count={c}"
        except Exception as e2:
            readable['profiles_mule_count'] = f"FAIL: {e2}"
    
    # Try scenarios
    try:
        cur.execute("SELECT scenario_id, scenario_name, crime_category, description, victim_city, victim_state, amount_lost_inr, status FROM scenarios LIMIT 5")
        rows = cur.fetchall()
        readable['scenarios'] = f"OK - {len(rows)} rows"
        for r in rows:
            print(f"  SCENARIO: id={r[0]} name={r[1]} status={r[7]}")
    except Exception as e:
        readable['scenarios'] = f"FAIL: {e}"

    # Try SCENARIO_001 specifically
    try:
        cur.execute("SELECT scenario_id, scenario_name, crime_category, description, victim_city, victim_state, amount_lost_inr, status FROM scenarios WHERE scenario_id = 'SCENARIO_001'")
        row = cur.fetchone()
        readable['SCENARIO_001'] = f"OK - {row}"
    except Exception as e:
        readable['SCENARIO_001'] = f"FAIL: {e}"

    # Try atms
    try:
        cur.execute("SELECT atm_id, bank_name, atm_name, latitude, longitude, state, city, atm_type, is_24x7, cash_availability_index, operational_status FROM atms LIMIT 3")
        rows = cur.fetchall()
        readable['atms'] = f"OK - {len(rows)} sample rows"
    except Exception as e:
        readable['atms'] = f"FAIL: {e}"
    
    # Try state_stats
    try:
        cur.execute("SELECT state_name, total_incidents, amount_reported_cr, incident_density, risk_tier FROM state_stats LIMIT 3")
        rows = cur.fetchall()
        readable['state_stats'] = f"OK - {len(rows)} sample rows"
    except Exception as e:
        readable['state_stats'] = f"FAIL: {e}"
        
    # Try transactions
    try:
        cur.execute("SELECT txn_id, chain_id, pattern_type, timestamp_ist, from_account_id, from_bank, to_account_id, to_bank, amount_inr, channel, is_laundering, hop_layer, is_terminal_cashout, crime_category FROM transactions LIMIT 3")
        rows = cur.fetchall()
        readable['transactions'] = f"OK - {len(rows)} sample rows"
    except Exception as e:
        readable['transactions'] = f"FAIL: {e}"
    
    conn.close()
    
    print("\n=== TABLE READABILITY SUMMARY ===")
    for k, v in readable.items():
        print(f"  {k}: {v}")

except Exception as e:
    print(f"CONNECT ERROR: {e}")
