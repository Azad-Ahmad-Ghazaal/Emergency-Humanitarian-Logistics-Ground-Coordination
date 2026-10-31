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


def test_invalid_priority_is_downgraded_and_signals_are_bounded(tmp_path):
    db = tmp_path / "safe.sqlite"
    init_db(db)
    add_incident({
        "location": "Shelter C",
        "report": "Need blankets",
        "priority": "URGENT-UNKNOWN",
        "signals": "not-a-list",
    }, db)
    row = list_incidents(db)[0]
    assert row["priority"] == "LOW"
    assert json.loads(row["signals_json"]) == []


def test_missing_required_fields_are_rejected(tmp_path):
    db = tmp_path / "required.sqlite"
    init_db(db)
    try:
        add_incident({"location": "Shelter D", "report": "  "}, db)
    except ValueError as exc:
        assert "report" in str(exc).lower()
    else:
        raise AssertionError("Empty incident report should be rejected")
