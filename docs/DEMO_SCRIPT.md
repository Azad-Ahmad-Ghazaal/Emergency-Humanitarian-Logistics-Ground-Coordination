# ReliefLens — 3-minute judge demo

## What to demonstrate

ReliefLens is an offline-first field-report intake prototype. It stores reports locally, supports a local Gemma 4 path, offers a separately labelled hosted Gemini API path, and keeps a transparent keyword fallback when model inference is unavailable.

## Demo sequence

1. Start the app with `streamlit run app.py`.
2. Open **New field report**.
3. Enter location: `North Shelter, Sector 4`.
4. Enter a sample report: `Several families report rising flood water near the shelter. The access road is blocked and clean drinking water is running low.`
5. Choose **Gemma 4 via Gemini API** only when internet and a valid `GEMINI_API_KEY` are available. Otherwise choose local Ollama only if the Gemma model has already been downloaded. If inference fails, show the explicitly labelled keyword fallback.
6. Optionally upload a clearly readable shelter-board photo and select **Handwritten shelter chart / chalkboard**. Explain that the model marks uncertain writing and a volunteer must verify the result.
7. Open **Incident board** and show the saved incident, priority, status, and CSV/JSON export.
8. Open **Integrations** and explain which tracks are implemented versus pending.

## Safety and honesty notes

- Never describe the prototype as a validated emergency dispatch, medical triage, structural engineering, or road-passability system.
- Do not claim local Gemma inference was demonstrated unless it was actually run on the demo machine.
- Hosted Gemini API use requires connectivity and is not offline operation.
- The optional voice module needs `pip install -r requirements-audio.txt` and first-run model download; it is not included in the core CI dependency set.
- Handwritten chart extraction is multimodal model-assisted transcription, not a dedicated OCR engine. A human must verify it.
- Snowflake assets are prompts and a schema-adaptable SQL template; a real Marketplace query still needs account access and evidence.
- Solana agent metadata is a draft; no on-chain registration or transaction signature is claimed.
- GitHub Copilot evidence must come from genuine Copilot usage. Do not invent screenshots or logs.

## Automated checks

The GitHub Actions CI workflow installs core dependencies, runs pytest, and compiles the Python source. The separate Gemini smoke workflow verifies hosted API access using the repository secret. These checks do not replace a live Streamlit UI test or local Ollama hardware test.
