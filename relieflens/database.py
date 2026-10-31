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
    with connect(db_path) as conn:
        cur = conn.execute("""INSERT INTO incidents
        (reporter, location, language, report, priority, summary, recommended_action, signals_json, ai_method)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
            data.get("reporter", ""), data["location"], data.get("language", "Unknown"),
            data["report"], data.get("priority", "LOW"), data.get("summary", ""),
            data.get("recommended_action", ""), json.dumps(data.get("signals", []), ensure_ascii=False),
            data.get("ai_method", "keyword_fallback")))
        conn.commit()
        return cur.lastrowid

def list_incidents(db_path=DB_PATH):
    with connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM incidents ORDER BY CASE priority WHEN 'CRITICAL' THEN 0 WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END, created_at DESC").fetchall()
        return [dict(row) for row in rows]
