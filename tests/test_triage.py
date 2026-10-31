from relieflens.triage import triage_text

def test_critical_report():
    assert triage_text("People trapped under collapsed building")["priority"] == "CRITICAL"

def test_supply_request():
    assert triage_text("Need food and clean water at shelter")["priority"] == "MEDIUM"

def test_unknown_report_defaults_low():
    assert triage_text("Situation being monitored")["priority"] == "LOW"
