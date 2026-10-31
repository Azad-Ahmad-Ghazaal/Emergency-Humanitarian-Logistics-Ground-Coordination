import json

from relieflens.database import add_incident, init_db, list_incidents


def test_incident_round_trip_and_priority_order(tmp_path):
    db = tmp_path / "test.sqlite"
    init_db(db)
    add_incident({
        "location": "Shelter A",
        "report": "Need drinking water",
        "priority": "MEDIUM",
        "summary": "Water shortage",
        "signals": ["water"],
        "ai_method": "keyword_fallback",
    }, db)
    add_incident({
        "location": "Bridge B",
        "report": "People trapped",
        "priority": "CRITICAL",
        "summary": "Possible trapped people",
        "signals": ["trapped"],
    }, db)

    rows = list_incidents(db)
    assert [row["priority"] for row in rows] == ["CRITICAL", "MEDIUM"]
    assert json.loads(rows[0]["signals_json"]) == ["trapped"]
    assert rows[0]["status"] == "OPEN"
