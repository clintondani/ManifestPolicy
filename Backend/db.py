# backend/db.py
import sqlite3
import json
from datetime import datetime

DB_NAME = "scanner.db"

def safe_json_load(value, default):
    if not value:
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return default



# ✅ Initialize database and create table if not exists
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        input_type TEXT,
        filename TEXT,
        shady_clauses TEXT,
        dpdp_violations TEXT,
        summary TEXT,
        timestamp TEXT,
        username TEXT
    )
    """)
    conn.commit()
    conn.close()


# ✅ Save a new scan report with optional username
def save_report(input_type, filename, shady_clauses, dpdp_violations, summary, username=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    summary_json = json.dumps(summary, ensure_ascii=False)

    cursor.execute("""
    INSERT INTO scans (input_type, filename, shady_clauses, dpdp_violations, summary, timestamp, username)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        input_type,
        filename,
        json.dumps(shady_clauses, ensure_ascii=False),
        json.dumps(dpdp_violations, ensure_ascii=False),
        summary_json,
        datetime.now().isoformat(),
        username
    ))

    conn.commit()
    conn.close()


# ✅ Fetch all scan reports (optionally filter by username)
def get_reports(username=None):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if username and username != "null":
        cursor.execute(
            "SELECT * FROM scans WHERE username = ? ORDER BY timestamp DESC",
            (username,)
        )
    else:
        cursor.execute("SELECT * FROM scans ORDER BY timestamp DESC")

    rows = cursor.fetchall()
    conn.close()

    reports = []
    for row in rows:
        reports.append({
            "id": row["id"],
            "input_type": row["input_type"],
            "filename": row["filename"],
            "summary": json.loads(row["summary"]) if row["summary"] else {},
            "shady_clauses": json.loads(row["shady_clauses"]) if row["shady_clauses"] else [],
            "dpdp_violations": json.loads(row["dpdp_violations"]) if row["dpdp_violations"] else [],
            "timestamp": row["timestamp"],
            "username": row["username"]
        })

    return reports

def get_report_by_id(report_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM scans WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row["id"],
        "input_type": row["input_type"],
        "filename": row["filename"],
        "summary": json.loads(row["summary"]) if row["summary"] else {},
        "shady_clauses": json.loads(row["shady_clauses"]) if row["shady_clauses"] else [],
        "dpdp_violations": json.loads(row["dpdp_violations"]) if row["dpdp_violations"] else [],
        "timestamp": row["timestamp"],
        "username": row["username"]
    }




