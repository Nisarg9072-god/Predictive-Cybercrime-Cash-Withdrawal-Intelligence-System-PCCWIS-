import pytest
import sqlite3
import os
from database.connection import get_dataset_connection, ReadOnlyDatabaseError

def test_dataset_connection_readonly():
    with pytest.raises(ReadOnlyDatabaseError):
        with get_dataset_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE _test_table (id INTEGER)")

def test_operational_connection_writable():
    from database.connection import get_operational_connection
    with get_operational_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS _test_table (id INTEGER)")
        cursor.execute("INSERT INTO _test_table VALUES (1)")
        conn.commit()
        
        cursor.execute("SELECT * FROM _test_table")
        res = cursor.fetchall()
        assert len(res) >= 1
        
        cursor.execute("DROP TABLE _test_table")
        conn.commit()
