import sqlite3
from database.connection import get_operational_connection

def init_db():
    with get_operational_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_sessions (
                session_id TEXT PRIMARY KEY,
                started_at TEXT,
                completed_at TEXT,
                target_type TEXT,
                target_id TEXT,
                status TEXT,
                iteration_count INTEGER DEFAULT 0,
                tool_call_count INTEGER DEFAULT 0,
                error TEXT,
                created_at TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS investigations (
                investigation_id TEXT PRIMARY KEY,
                session_id TEXT,
                subject_type TEXT,
                subject_id TEXT,
                objective TEXT,
                status TEXT,
                started_at TEXT,
                completed_at TEXT,
                FOREIGN KEY (session_id) REFERENCES agent_sessions(session_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS observations (
                observation_id TEXT PRIMARY KEY,
                investigation_id TEXT,
                source TEXT,
                observation_type TEXT,
                summary TEXT,
                confidence REAL,
                created_at TEXT,
                FOREIGN KEY (investigation_id) REFERENCES investigations(investigation_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hypotheses (
                hypothesis_id TEXT PRIMARY KEY,
                investigation_id TEXT,
                description TEXT,
                category TEXT,
                confidence REAL,
                status TEXT,
                supporting_observations TEXT,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (investigation_id) REFERENCES investigations(investigation_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_decisions (
                decision_id TEXT PRIMARY KEY,
                investigation_id TEXT,
                iteration INTEGER,
                observation_summary TEXT,
                selected_tool TEXT,
                reason_summary TEXT,
                result_summary TEXT,
                created_at TEXT,
                FOREIGN KEY (investigation_id) REFERENCES investigations(investigation_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS findings (
                finding_id TEXT PRIMARY KEY,
                investigation_id TEXT,
                title TEXT,
                category TEXT,
                severity TEXT,
                confidence REAL,
                description TEXT,
                evidence_summary TEXT,
                remediation TEXT,
                status TEXT,
                created_at TEXT,
                FOREIGN KEY (investigation_id) REFERENCES investigations(investigation_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_events (
                event_id TEXT PRIMARY KEY,
                session_id TEXT,
                event_type TEXT,
                component TEXT,
                status TEXT,
                metadata TEXT,
                created_at TEXT,
                FOREIGN KEY (session_id) REFERENCES agent_sessions(session_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_assessments (
                risk_assessment_id TEXT PRIMARY KEY,
                investigation_id TEXT,
                iteration INTEGER,
                risk_score REAL,
                risk_level TEXT,
                confidence REAL,
                indicator_ids TEXT,
                evidence_ids TEXT,
                created_at TEXT,
                FOREIGN KEY (investigation_id) REFERENCES investigations(investigation_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evidence_items (
                evidence_id TEXT NOT NULL,
                investigation_id TEXT,
                source_type TEXT,
                source_id TEXT,
                observed_field TEXT,
                observed_value TEXT,
                description TEXT,
                confidence REAL,
                timestamp TEXT,
                hash TEXT UNIQUE NOT NULL,
                classification TEXT,
                indicator_name TEXT,
                parent_evidence_id TEXT,
                created_at TEXT,
                FOREIGN KEY (investigation_id) REFERENCES investigations(investigation_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                report_id TEXT PRIMARY KEY,
                investigation_id TEXT,
                scenario_id TEXT,
                mode TEXT,
                pdf_path TEXT,
                sha256 TEXT,
                generated_at TEXT,
                FOREIGN KEY (investigation_id) REFERENCES investigations(investigation_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS finding_transitions (
                transition_id TEXT PRIMARY KEY,
                finding_id TEXT,
                investigation_id TEXT,
                from_status TEXT,
                to_status TEXT,
                reason TEXT,
                transitioned_at TEXT,
                transitioned_by TEXT,
                FOREIGN KEY (investigation_id) REFERENCES investigations(investigation_id)
            )
        ''')

        conn.commit()
        print("[DATABASE] Operational database initialized.")

if __name__ == "__main__":
    init_db()
