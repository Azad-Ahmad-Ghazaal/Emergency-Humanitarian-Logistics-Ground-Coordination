from relieflens.gemma import _parse


def test_parse_gemma_response_normalizes_priority_and_signals():
    result = _parse(
        "PRIORITY: high\nLANGUAGE: Urdu\nSUMMARY: Flood near shelter\n"
        "ACTION: Verify access\nSIGNALS: flood, blocked road",
        "test_model",
    )
    assert result["priority"] == "HIGH"
    assert result["language"] == "Urdu"
    assert result["summary"] == "Flood near shelter"
    assert result["recommended_action"] == "Verify access"
    assert result["signals"] == ["flood", "blocked road"]
    assert result["ai_method"] == "test_model"


def test_parse_unknown_priority_falls_back_safely():
    result = _parse("PRIORITY: EXTREME\nSUMMARY: Unverified", "test_model")
    assert result["priority"] == "LOW"
    assert result["summary"] == "Unverified"
    assert result["recommended_action"] == "Human responder review required."
