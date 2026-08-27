import sqlite3
import os

db_path = 'data/synthetic/CYBER_INTERCEPT_FULL_DATASET/cyber_intercept.db'

# Determine which tree (table) is Tree 29
try:
    conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
    cur = conn.cursor()
    
    # rootpage identifies which B-tree is Tree 29
    cur.execute("SELECT name, rootpage, type FROM sqlite_master ORDER BY rootpage")
    print("Table rootpages:")
    for r in cur.fetchall():
        print(f"  rootpage={r[1]:>6}  type={r[2]:8}  name={r[0]}")
    
    # Sample first 3 rows from every table to see what can be read
    print("\nSample rows per table:")
    for table in ['transactions', 'profiles', 'scenarios', 'atms', 'districts', 'state_stats']:
        try:
            cur.execute(f"SELECT * FROM {table} LIMIT 3")
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]
            print(f"\n  {table} columns: {cols}")
            for row in rows:
                print(f"    {dict(zip(cols, row))}")
        except Exception as e:
            print(f"\n  {table}: FETCH ERROR - {e}")

    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
