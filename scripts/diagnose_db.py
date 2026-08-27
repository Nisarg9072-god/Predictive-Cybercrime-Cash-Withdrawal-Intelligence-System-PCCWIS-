import sqlite3
import os

db_path = 'data/synthetic/CYBER_INTERCEPT_FULL_DATASET/cyber_intercept.db'
print(f'Exists: {os.path.exists(db_path)}')
print(f'Size: {os.path.getsize(db_path) / (1024**3):.2f} GB')

try:
    conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
    cur = conn.cursor()
    
    # List tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    print(f'Tables: {tables}')
    
    # Per-table integrity
    for table in tables:
        try:
            cur.execute(f"SELECT count(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"  {table}: {count} rows - OK")
        except Exception as te:
            print(f"  {table}: ERROR - {te}")
            
    # PRAGMA integrity_check
    print("\nRunning PRAGMA integrity_check (first 20 lines)...")
    cur.execute("PRAGMA integrity_check")
    results = cur.fetchmany(20)
    for r in results:
        print(f"  {r[0]}")
        
    conn.close()
except Exception as e:
    print(f'CONNECT ERROR: {e}')
