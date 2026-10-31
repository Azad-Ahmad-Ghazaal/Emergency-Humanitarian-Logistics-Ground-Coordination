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
            status TEXT NOT NULL DEFAULT 'OPEN',
            latitude REAL, longitude REAL,
            status_updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
        # Lightweight migrations keep existing deployed SQLite databases compatible.
        columns = {row[1] for row in conn.execute("PRAGMA table_info(incidents)").fetchall()}
        for name, sql_type in (("latitude", "REAL"), ("longitude", "REAL"), ("status_updated_at", "TEXT")):
            if name not in columns:
                conn.execute(f"ALTER TABLE incidents ADD COLUMN {name} {sql_type}")
        conn.execute("""CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, category TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            unit TEXT NOT NULL DEFAULT 'items',
            location TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
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
        (reporter, location, language, report, priority, summary, recommended_action, signals_json, ai_method, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
            str(data.get("reporter", ""))[:120], location, str(data.get("language", "Unknown"))[:80],
            report[:20000], priority, str(data.get("summary", ""))[:4000],
            str(data.get("recommended_action", ""))[:2000], json.dumps(signals, ensure_ascii=False),
            str(data.get("ai_method", "keyword_fallback"))[:80],
            float(data["latitude"]) if data.get("latitude") not in (None, "") else None,
            float(data["longitude"]) if data.get("longitude") not in (None, "") else None))
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
            "UPDATE incidents SET status = ?, status_updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, int(incident_id)),
        )
        conn.commit()
        return cur.rowcount > 0


def list_resources(db_path=DB_PATH):
    with connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM resources ORDER BY category, name").fetchall()
        return [dict(row) for row in rows]


def save_resource(name, category, quantity, unit, location, resource_id=None, db_path=DB_PATH):
    name = str(name).strip()[:120]
    category = str(category).strip()[:80]
    unit = str(unit).strip()[:40] or "items"
    location = str(location).strip()[:160]
    quantity = max(0, min(int(quantity), 100000000))
    if not name or not category:
        raise ValueError("Resource name and category are required.")
    with connect(db_path) as conn:
        if resource_id:
            conn.execute("""UPDATE resources SET name=?, category=?, quantity=?, unit=?, location=?,
                updated_at=CURRENT_TIMESTAMP WHERE id=?""",
                (name, category, quantity, unit, location, int(resource_id)))
        else:
            conn.execute("""INSERT INTO resources (name, category, quantity, unit, location)
                VALUES (?, ?, ?, ?, ?)""", (name, category, quantity, unit, location))
        conn.commit()


def delete_resource(resource_id, db_path=DB_PATH):
    with connect(db_path) as conn:
        conn.execute("DELETE FROM resources WHERE id=?", (int(resource_id),))
        conn.commit()


def find_possible_duplicates(location, report, db_path=DB_PATH):
    """Conservative same-location/token-overlap hints; never auto-merges reports."""
    import re
    words = lambda value: {w for w in re.findall(r"\w+", str(value).lower()) if len(w) > 3}
    incoming = words(report)
    loc = " ".join(str(location).lower().split())
    matches = []
    for item in list_incidents(db_path):
        old_loc = " ".join(str(item.get("location", "")).lower().split())
        old_words = words(item.get("report", ""))
        overlap = len(incoming & old_words) / max(1, len(incoming | old_words))
        if loc and loc == old_loc and overlap >= 0.18:
            matches.append({"id": item["id"], "location": item["location"], "priority": item["priority"],
                            "status": item["status"], "similarity": round(overlap * 100)})
    return matches
