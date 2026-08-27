import sqlite3
import os
import contextlib
from pathlib import Path
from config import config

class ReadOnlyDatabaseError(Exception):
    pass

@contextlib.contextmanager
def get_dataset_connection():
    """
    Returns a read-only connection to the master dataset.
    Prevents accidental writes.
    """
    db_path = config.DATASET_DB_PATH
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Dataset database not found at {db_path}")
    
    # Use URI to enforce read-only mode at the SQLite driver level
    # Convert path to absolute and ensure forward slashes for URI
    abs_path = os.path.abspath(db_path).replace("\\", "/")
    uri = f"file:{abs_path}?mode=ro"
    
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    except sqlite3.OperationalError as e:
        if "readonly database" in str(e).lower():
            raise ReadOnlyDatabaseError("Attempted to modify the read-only master dataset!") from e
        raise
    finally:
        conn.close()

@contextlib.contextmanager
def get_operational_connection():
    """
    Returns a read-write connection to the operational database.
    """
    db_path = config.OPERATIONAL_DB_PATH
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
