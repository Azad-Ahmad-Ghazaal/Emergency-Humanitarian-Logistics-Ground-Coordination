import os

SYSTEM_PROMPT = """You are ReliefLens, an emergency logistics information assistant.
Preserve the report's original language. Return exactly these labels:
PRIORITY: CRITICAL, HIGH, MEDIUM, or LOW
LANGUAGE: detected language
SUMMARY: concise factual summary
ACTION: practical next coordination step
SIGNALS: comma-separated evidence
Never invent coordinates, casualties, road conditions, or supplies. Mark unknown facts UNKNOWN.
This is decision support only; human responders make all operational decisions."""

def _parse(raw, method):
    fields = {}
    for line in (raw or "").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip().upper()] = value.strip()
    priority = fields.get("PRIORITY", "LOW").upper()
    if priority not in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}:
        priority = "LOW"
    return {
        "priority": priority,
        "language": fields.get("LANGUAGE", "Unknown"),
        "summary": fields.get("SUMMARY", raw[:600]),
        "recommended_action": fields.get("ACTION", "Human responder review required."),
        "signals": [s.strip() for s in fields.get("SIGNALS", "").split(",") if s.strip()],
        "ai_method": method,
        "raw_analysis": raw,
    }

def analyze_text(report, mode="Local Gemma 4 (Ollama)"):
    if mode.startswith("Local"):
        import ollama
        response = ollama.chat(
            model=os.getenv("OLLAMA_MODEL", "gemma4:e4b"),
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                      {"role": "user", "content": report}],
            options={"temperature": 0.1},
        )
        return _parse(response["message"]["content"], "local_ollama_gemma4")
    from google import genai
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model=os.getenv("GEMMA_GEMINI_MODEL", "gemma-4-26b-a4b-it"),
        contents=SYSTEM_PROMPT + "\n\nINCIDENT REPORT:\n" + report,
    )
    return _parse(response.text or "", "gemini_api_gemma4")

def analyze_image(image_path):
    import ollama
    response = ollama.chat(
        model=os.getenv("OLLAMA_MODEL", "gemma4:e4b"),
        messages=[{"role": "user",
                   "content": "Describe visible disaster damage and access hazards. Do not claim structural integrity from an image.",
                   "images": [str(image_path)]}],
        options={"temperature": 0.1},
    )
    return response["message"]["content"]
