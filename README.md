# ReliefLens — Multilingual Disaster Relief & Ground Coordination

Offline-first prototype for emergency field reporting when regional connectivity is unreliable. It accepts multilingual text, optionally analyses rescue-scene photos, prioritizes reports, and stores incidents in a local SQLite register.

> Safety: This is a decision-support prototype, not an emergency dispatch system or structural-engineering assessment. Human responders must verify every alert.

## Quick start

Requirements: Python 3.10+, Ollama, and hardware capable of running your selected Gemma 4 variant.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
# Optional offline voice transcription
pip install -r requirements-audio.txt
# Copy .env.example to .env
ollama pull gemma4:e2b
streamlit run app.py
```

## Exact Gemma 4 integrations

### Local Gemma 4 — Ollama

Implementation: relieflens/gemma.py, analyze_text() local branch and analyze_image().
- Uses Ollama local inference, default model gemma4:e2b (configurable with OLLAMA_MODEL).
- Processes report text and uploaded image inputs locally.
- Once model weights are downloaded, local inference does not require a Gemini API key.
- Download the model before deployment in a disconnected disaster area.

### Hosted Gemma 4 — Gemini API

Implementation: relieflens/gemma.py, analyze_text() hosted branch.
- Uses Google's official google-genai Python SDK.
- Exact default model identifier: gemma-4-26b-a4b-it (configurable with GEMMA_GEMINI_MODEL).
- Set GEMINI_API_KEY in .env.
- This is a hosted API and is NOT offline. The hosted path supports both report text and uploaded image analysis. Image files are uploaded to the Gemini API for processing, so this path requires internet connectivity and should not be used for disconnected field operations.

Official guide: https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api

## Hosted image analysis

The Gemini API adapter uploads the selected image with the Google GenAI SDK and sends it to the same Gemma 4 model used for text. Local mode instead passes the image directly to Ollama. These are separate execution paths.

## Offline voice memo transcription

An optional local CPU transcription path is available through `faster-whisper`. Install it separately with `pip install -r requirements-audio.txt`; upload a WAV, MP3, M4A, OGG, or FLAC voice memo in the field-report form. The default model is Whisper `base` with CPU `int8` inference (configurable via `WHISPER_MODEL` and `WHISPER_COMPUTE_TYPE`). The first run downloads model weights, so pre-cache them before going offline. Transcription quality varies by dialect, noise, and speaker; volunteers must review the transcript before treating it as a factual report.

## Offline data

SQLite database relieflens_incidents.db is created on first launch. The incident board exports CSV and JSON. Protect devices and exported files because humanitarian reports may contain sensitive data.

## Triage

Gemma output is parsed into priority, summary, action, and evidence signals. If inference fails, a transparent keyword fallback is used and labelled keyword_fallback. This fallback is not AI and is not a validated risk classifier.

## Challenge integrations and evidence

- Snowflake CoCo: workflow assets are in `snowflake/COCO_PROMPTS.md` and `snowflake/relieflens_infrastructure_template.sql`. CoCo must inspect a real Marketplace listing and adapt/run the SQL against verified schemas. No live Snowflake account or Marketplace query has been executed from this repository yet.
- Solana Agent Registry: NOT registered yet. Add the public agent profile and transaction/signature link only after successful on-chain registration. Never commit private keys or seed phrases.
- GitHub Copilot: evidence pending. Add genuine screenshots or sanitized logs showing the real Copilot prompt, response, and resulting code/debugging outcome. Do not fabricate evidence.
- Handwritten chart OCR: not integrated yet; the Gemma image path can provide visual observations, but no dedicated handwriting extraction workflow is claimed.

## Tests

```bash
pytest -q
```

## License

MIT. See LICENSE.
