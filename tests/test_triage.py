from relieflens.triage import triage_text

def test_critical_report():
    assert triage_text("People trapped under collapsed building")["priority"] == "CRITICAL"

def test_supply_request():
    assert triage_text("Need food and clean water at shelter")["priority"] == "MEDIUM"

def test_unknown_report_defaults_low():
    assert triage_text("Situation being monitored")["priority"] == "LOW"


def test_urdu_critical_report():
    result = triage_text("عمارت کے ملبے میں لوگ پھنسے ہوئے ہیں")
    assert result["priority"] == "CRITICAL"
    assert result["method"] == "keyword_fallback"


def test_urdu_flood_report_is_high():
    result = triage_text("علاقے میں شدید سیلاب ہے")
    assert result["priority"] == "HIGH"
    assert "سیلاب" in result["signals"]


def test_critical_signal_takes_precedence_over_supply_need():
    result = triage_text("People trapped and need food and water")
    assert result["priority"] == "CRITICAL"
