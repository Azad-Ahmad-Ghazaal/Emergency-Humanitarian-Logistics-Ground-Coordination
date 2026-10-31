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

IMAGE_PROMPT = """Describe only visible disaster damage and access hazards in this image.
Do not infer hidden damage, structural integrity, casualty counts, or safe passage.
Separate direct observations from uncertainty. Human responders must verify on site."""

CHALKBOARD_PROMPT = """Read this photograph of a handwritten emergency shelter chart or chalkboard.
Transcribe only text and numbers that are visibly legible. Preserve the original language and script.
Return:
TRANSCRIPTION: line-by-line transcription; mark unreadable spans as [UNCLEAR]
LANGUAGE: likely language(s), or UNKNOWN
POSSIBLE_COUNTS: only clearly legible quantities, each tied to its visible label
UNCERTAINTIES: list ambiguous characters, damaged/obscured areas, and uncertain readings
Do not guess missing words, names, locations, quantities, medical details, or needs.
Do not convert uncertain writing into facts. A human volunteer must verify every extracted item before operational use."""

def _parse(raw, method):
    raw = raw or ""
    fields = {}
    for line in raw.splitlines():
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

def _gemini_client():
    from google import genai
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            api_key = ""
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to your environment, .env file, or Streamlit secrets.")
    return genai.Client(api_key=api_key)

def analyze_text(report, mode="Local Gemma 4 (Ollama)"):
    if mode.startswith("Local"):
        import ollama
        response = ollama.chat(
            model=os.getenv("OLLAMA_MODEL", "gemma4:e2b"),
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                      {"role": "user", "content": report}],
            options={"temperature": 0.1},
        )
        return _parse(response["message"]["content"], "local_ollama_gemma4")
    client = _gemini_client()
    response = client.models.generate_content(
        model=os.getenv("GEMMA_GEMINI_MODEL", "gemma-4-26b-a4b-it"),
        contents=SYSTEM_PROMPT + "\n\nINCIDENT REPORT:\n" + report,
    )
    return _parse(response.text, "gemini_api_gemma4")

def analyze_image(image_path, mode="Local Gemma 4 (Ollama)", purpose="scene"):
    prompt = CHALKBOARD_PROMPT if purpose == "chalkboard" else IMAGE_PROMPT
    if mode.startswith("Local"):
        import ollama
        response = ollama.chat(
            model=os.getenv("OLLAMA_MODEL", "gemma4:e2b"),
            messages=[{"role": "user", "content": prompt,
                       "images": [str(image_path)]}],
            options={"temperature": 0.1},
        )
        return response["message"]["content"]

    client = _gemini_client()
    uploaded = client.files.upload(file=str(image_path))
    response = client.models.generate_content(
        model=os.getenv("GEMMA_GEMINI_MODEL", "gemma-4-26b-a4b-it"),
        contents=[uploaded, prompt],
    )
    return response.text or "No image observations returned by Gemma 4."
