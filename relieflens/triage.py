RULES = {
    "CRITICAL": ["trapped", "collapsed", "collapse", "missing", "severe bleeding", "unconscious", "fire", "drowning", "بے ہوش", "ملبہ", "پھنسے"],
    "HIGH": ["injured", "injury", "flood", "washed out", "bridge damaged", "blocked road", "evacuation", "سیلاب", "پل ٹوٹ"],
    "MEDIUM": ["food", "water", "medicine", "shelter", "supplies", "راشن", "پانی", "ادویات"],
}

def triage_text(text: str) -> dict:
    normalized = (text or "").lower()
    for priority in ("CRITICAL", "HIGH", "MEDIUM"):
        matches = [term for term in RULES[priority] if term in normalized]
        if matches:
            return {"priority": priority, "signals": matches, "method": "keyword_fallback"}
    return {"priority": "LOW", "signals": [], "method": "keyword_fallback"}
