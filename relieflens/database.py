import json
import sqlite3
from pathlib import Path

DB_PATH = Path("relieflens_incidents.db")

def connect(db_path=DB_PATH):
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path=DB_PATH):
    with connect(db_path) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            reporter TEXT, location TEXT NOT NULL, language TEXT,
            report TEXT NOT NULL, priority TEXT NOT NULL, summary TEXT,
            recommended_action TEXT, signals_json TEXT NOT NULL DEFAULT '[]',
            ai_method TEXT NOT NULL DEFAULT 'keyword_fallback',
            status TEXT NOT NULL DEFAULT 'OPEN')""")
        conn.commit()

def add_incident(data, db_path=DB_PATH):
    # Validate and bound untrusted model/user fields before persistence.
    location = str(data.get("location") or "").strip()
    report = str(data.get("report") or "").strip()
    if not location:
        raise ValueError("Incident location is required.")
    if not report:
        raise ValueError("Incident report text is required.")
    priority = str(data.get("priority") or "LOW").upper()
    if priority not in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}:
        priority = "LOW"
    raw_signals = data.get("signals", [])
    if not isinstance(raw_signals, (list, tuple)):
        raw_signals = []
    signals = [str(item).strip()[:200] for item in raw_signals if str(item).strip()][:50]
    with connect(db_path) as conn:
        cur = conn.execute("""INSERT INTO incidents
        (reporter, location, language, report, priority, summary, recommended_action, signals_json, ai_method)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
            str(data.get("reporter", ""))[:120], location, str(data.get("language", "Unknown"))[:80],
            report[:20000], priority, str(data.get("summary", ""))[:4000],
            str(data.get("recommended_action", ""))[:2000], json.dumps(signals, ensure_ascii=False),
            str(data.get("ai_method", "keyword_fallback"))[:80]))
        conn.commit()
        return cur.lastrowid

def list_incidents(db_path=DB_PATH):
    with connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM incidents ORDER BY CASE priority WHEN 'CRITICAL' THEN 0 WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END, created_at DESC").fetchall()
        return [dict(row) for row in rows]


def update_incident_status(incident_id, status, db_path=DB_PATH):
    """Update the operational status of an incident using an allow-listed value."""
    allowed = {"OPEN", "IN_PROGRESS", "RESOLVED"}
    status = str(status).upper()
    if status not in allowed:
        raise ValueError("Unsupported incident status.")
    with connect(db_path) as conn:
        cur = conn.execute(
            "UPDATE incidents SET status = ? WHERE id = ?",
            (status, int(incident_id)),
        )
        conn.commit()
        return cur.rowcount > 0
