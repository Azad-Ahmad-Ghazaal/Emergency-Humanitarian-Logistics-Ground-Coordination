import json
import os
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from relieflens.database import add_incident, init_db, list_incidents
from relieflens.gemma import analyze_image, analyze_text
from relieflens.triage import triage_text

load_dotenv()
st.set_page_config(page_title="ReliefLens | Disaster Coordination", page_icon="🆘", layout="wide")
init_db()
st.title("🆘 ReliefLens")
st.caption("Offline-first multilingual disaster relief • Emergency logistics & ground coordination")
st.warning("Prototype decision support only. Verify every report with trained responders. Never use this tool as the sole basis for rescue, evacuation, or structural-safety decisions.")

incidents = list_incidents()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total reports", len(incidents))
c2.metric("Critical", sum(x["priority"] == "CRITICAL" for x in incidents))
c3.metric("High", sum(x["priority"] == "HIGH" for x in incidents))
c4.metric("Open", sum(x["status"] == "OPEN" for x in incidents))

tab1, tab2, tab3 = st.tabs(["➕ New field report", "🗺️ Incident board", "🔧 Integrations"])
with tab1:
    st.subheader("Submit a field report")
    with st.form("incident_form"):
        a, b = st.columns(2)
        reporter = a.text_input("Volunteer / team ID (optional)")
        location = b.text_input("Location / landmark *")
        language = st.selectbox("Report language", ["Auto-detect", "Urdu", "English", "Punjabi", "Pashto", "Sindhi", "Other"])
        report = st.text_area("Raw field report *", height=150, placeholder="Paste field notes or a voice transcription. Preserve original wording.")
        photo = st.file_uploader("Rescue-scene photo (optional)", type=["png", "jpg", "jpeg"])
        engine = st.radio("Analysis engine", ["Local Gemma 4 (Ollama)", "Gemma 4 via Gemini API"], horizontal=True)
        submitted = st.form_submit_button("Analyse & save report", type="primary")
    if submitted:
        if not location.strip() or not report.strip():
            st.error("Location and report are required.")
        else:
            with st.spinner("Analysing field report..."):
                try:
                    result = analyze_text(report, engine)
                except Exception as exc:
                    st.warning("Gemma unavailable; saving transparent keyword fallback. Details: " + str(exc))
                    fallback = triage_text(report)
                    result = {"priority": fallback["priority"], "language": language,
                              "summary": "AI analysis unavailable. Human review required.",
                              "recommended_action": "Contact the local response coordinator and verify on the ground.",
                              "signals": fallback["signals"], "ai_method": "keyword_fallback"}
                image_notes = ""
                if photo is not None:
                    suffix = Path(photo.name).suffix or ".jpg"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(photo.getvalue())
                        temp_path = tmp.name
                    try:
                        image_notes = analyze_image(temp_path, engine)
                    except Exception as exc:
                        image_notes = "Image analysis unavailable: " + str(exc)
                    finally:
                        Path(temp_path).unlink(missing_ok=True)
                record = {**result, "reporter": reporter, "location": location.strip(),
                          "language": result.get("language", language), "report": report}
                if image_notes:
                    record["summary"] = record.get("summary", "") + "\nIMAGE OBSERVATIONS: " + image_notes
                incident_id = add_incident(record)
            st.success("Report saved locally as incident #" + str(incident_id))
            st.markdown("**Priority:** " + record["priority"])
            st.write(record.get("summary"))
            st.write("**Recommended next step:**", record.get("recommended_action"))
            if image_notes:
                st.write("**Image observations:**", image_notes)
            st.caption("Analysis method: " + record.get("ai_method", "unknown"))

with tab2:
    st.subheader("Ground coordination incident board")
    if incidents:
        df = pd.DataFrame(incidents)
        st.dataframe(df[["id", "created_at", "location", "language", "priority", "summary", "status", "ai_method"]],
                     use_container_width=True, hide_index=True)
        st.download_button("Export CSV", df.to_csv(index=False).encode("utf-8"),
                           "relieflens_incidents.csv", "text/csv")
        st.download_button("Export JSON", json.dumps(incidents, ensure_ascii=False, indent=2),
                           "relieflens_incidents.json", "application/json")
    else:
        st.info("No reports yet. Add a field report to populate the board.")

with tab3:
    st.subheader("Integration status")
    st.markdown("""
| Track | Status in this starter build |
|---|---|
| Local Gemma 4 | Ollama adapter for text and images; local model must be installed |
| Gemini API Gemma 4 | Hosted text and image adapter; API key + internet required |
| Offline incident store | SQLite |
| Multilingual reports | Original text passed to model; no forced translation |
| Voice transcription | Not integrated yet |
| Handwritten chart OCR | Not integrated yet |
| Snowflake CoCo | Not integrated yet |
| Solana Agent Registry | Not registered yet |
| Copilot evidence | Must be captured from actual Copilot use |
""")
    st.code("ollama pull gemma4:e2b\nstreamlit run app.py", language="bash")
    st.info("Hosted mode: configure GEMINI_API_KEY in .env or your hosting provider secrets. Local mode requires Ollama and a downloaded Gemma model.")

st.divider()
st.caption("ReliefLens • Prototype for humanitarian coordination • Verify every alert with human responders.")
