import json
import os
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from relieflens.audio import transcribe_audio
from relieflens.database import add_incident, init_db, list_incidents
from relieflens.gemma import analyze_image, analyze_text
from relieflens.triage import triage_text

load_dotenv()
st.set_page_config(page_title="ReliefLens | Disaster Coordination", page_icon="🆘", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
:root { --rl-bg:#071525; --rl-panel:#10263b; --rl-line:rgba(132,190,211,.20); --rl-teal:#39dfc0; }
.stApp {background:radial-gradient(ellipse at 15% 0%,#153b50 0%,transparent 38%),linear-gradient(145deg,#071525 0%,#0b1d30 58%,#10283a 100%); color:#eef5fb; font-family:'DM Sans',sans-serif;}
.block-container {padding-top:1.35rem; padding-bottom:2rem; max-width:1450px;}
h1,h2,h3 {color:#f5f9ff !important; letter-spacing:-.025em;}
h1 {font-size:2.55rem !important; font-weight:800 !important;}
h2 {font-size:1.55rem !important; font-weight:750 !important;}
h3 {font-size:1.15rem !important; font-weight:700 !important;}
p, label, .stMarkdown {color:#d8e5ef;}
[data-testid="stMetric"] {background:linear-gradient(145deg,rgba(24,55,76,.94),rgba(14,35,54,.94)); border:1px solid var(--rl-line); padding:17px 19px; border-radius:16px; box-shadow:0 8px 24px rgba(0,0,0,.13);}
[data-testid="stMetricLabel"] {color:#a9c3d6; font-weight:600;}
[data-testid="stMetricValue"] {color:var(--rl-teal); font-weight:800;}
[data-testid="stMetricDelta"] {color:#a8d8cf;}
.stTabs [data-baseweb="tab-list"] {gap:9px; border-bottom:1px solid var(--rl-line);}
.stTabs [data-baseweb="tab"] {height:48px; padding:0 18px; border-radius:11px 11px 0 0; color:#b9cbd9; font-weight:700;}
.stTabs [aria-selected="true"] {background:rgba(57,223,192,.12); color:#65efd3 !important;}
input,textarea,[data-baseweb="select"] > div {background-color:#10263b !important; border-color:#31516a !important; border-radius:10px !important; color:#f3f8fc !important;}
[data-testid="stFileUploader"] section {background:rgba(16,38,59,.7); border:1px dashed #477086; border-radius:13px;}
div.stButton > button, div.stDownloadButton > button, div.stFormSubmitButton > button {border-radius:11px; min-height:42px; font-weight:700; border:1px solid #37657a; background:#15364a; color:#eaf7f5; transition:all .15s ease;}
div.stButton > button[kind="primary"], div.stFormSubmitButton > button[kind="primary"] {background:linear-gradient(100deg,#008f83,#10b99c); border:0; color:white; box-shadow:0 6px 18px rgba(0,185,156,.18);}
div.stButton > button:hover, div.stDownloadButton > button:hover {border-color:#4de2c4; color:#fff;}
[data-testid="stDataFrame"] {border:1px solid var(--rl-line); border-radius:13px; overflow:hidden;}
[data-testid="stAlert"] {border-radius:12px; border:1px solid var(--rl-line);}
hr {border-color:var(--rl-line);}
small,.stCaption {color:#9db4c6 !important;}
</style>
""", unsafe_allow_html=True)
init_db()
st.markdown("""
<div style="background:linear-gradient(112deg,rgba(18,55,75,.98),rgba(10,35,54,.96));border:1px solid rgba(89,220,199,.25);border-radius:22px;padding:26px 30px;margin:4px 0 18px 0;box-shadow:0 16px 36px rgba(0,0,0,.18)">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:9px">
    <span style="font-size:30px">🆘</span><span style="font-size:29px;font-weight:800;letter-spacing:-1px;color:#f4fbff">ReliefLens</span>
    <span style="margin-left:8px;padding:5px 11px;border-radius:20px;background:rgba(57,223,192,.13);color:#63ebd1;font-size:11px;font-weight:800;letter-spacing:1px">FIELD COORDINATION</span>
  </div>
  <div style="font-size:21px;font-weight:700;color:#e8f5fb;margin-bottom:7px">From field reports to clearer relief priorities.</div>
  <div style="font-size:14px;line-height:1.6;color:#b7ccda;max-width:900px">Multilingual, offline-first decision support for organizing text reports, voice notes and field images into a prioritized incident board.</div>
</div>
""", unsafe_allow_html=True)
with st.expander("⚠️ Prototype safety notice — please read"):
    st.warning("Decision support only. Verify every report with trained responders. Never use this tool as the sole basis for rescue, evacuation, or structural-safety decisions.")

incidents = list_incidents()
if st.session_state.get("saved_notice"):
    st.success(st.session_state.pop("saved_notice"))
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total reports", len(incidents))
c2.metric("Critical", sum(x["priority"] == "CRITICAL" for x in incidents))
c3.metric("High", sum(x["priority"] == "HIGH" for x in incidents))
c4.metric("Open", sum(x["status"] == "OPEN" for x in incidents))

tab1, tab2, tab3 = st.tabs(["➕ New field report", "🗺️ Incident board", "🔧 Integrations"])
with tab1:
    st.subheader("New field report")
    st.caption("Add the location and report first. Attach a photo or voice memo when available.")
    with st.form("incident_form"):
        a, b = st.columns(2)
        reporter = a.text_input("Volunteer / team ID (optional)")
        location = b.text_input("Location / landmark *")
        language = st.selectbox("Report language", ["Auto-detect", "Urdu", "English", "Punjabi", "Pashto", "Sindhi", "Other"])
        report = st.text_area("Raw field report *", height=150, placeholder="Paste field notes or a voice transcription. Preserve original wording.")
        photo = st.file_uploader("Photo (optional)", type=["png", "jpg", "jpeg"])
        photo_purpose = st.selectbox("Photo type", ["Rescue scene / damaged route", "Handwritten shelter chart / chalkboard"])
        audio = st.file_uploader("Voice memo (optional, offline transcription)", type=["wav", "mp3", "m4a", "ogg", "flac"])
        cloud_key_available = bool(os.getenv("GEMINI_API_KEY"))
        try:
            cloud_key_available = cloud_key_available or bool(st.secrets.get("GEMINI_API_KEY", ""))
        except Exception:
            pass
        default_engine = 1 if cloud_key_available else 0
        engine = st.radio("Analysis engine", ["Local Gemma 4 (Ollama)", "Gemma 4 via Gemini API"], index=default_engine, horizontal=True)
        submitted = st.form_submit_button("Analyse & save report", type="primary")
    if submitted:
        if not location.strip() or (not report.strip() and audio is None):
            st.error("Location and either report text or a voice memo are required.")
        elif len(report) > 10000:
            st.error("Report is too long. Please keep it under 10,000 characters.")
        elif photo is not None and len(photo.getvalue()) > 10 * 1024 * 1024:
            st.error("Photo is larger than 10 MB. Please upload a smaller image.")
        elif audio is not None and len(audio.getvalue()) > 20 * 1024 * 1024:
            st.error("Voice memo is larger than 20 MB. Please upload a smaller audio file.")
        else:
            if audio is not None:
                with st.spinner("Transcribing voice memo locally..."):
                    audio_suffix = Path(audio.name).suffix or ".wav"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=audio_suffix) as audio_tmp:
                        audio_tmp.write(audio.getvalue())
                        audio_path = audio_tmp.name
                    try:
                        transcript = transcribe_audio(audio_path)
                        if not report.strip():
                            report = transcript["text"]
                        language = transcript["language"]
                        st.info("Local voice transcription (" + transcript["language"] + "): " + transcript["text"])
                    except Exception as exc:
                        st.error("Voice transcription unavailable: " + str(exc))
                        st.stop()
                    finally:
                        Path(audio_path).unlink(missing_ok=True)
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
                image_error = ""
                if photo is not None:
                    suffix = Path(photo.name).suffix or ".jpg"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(photo.getvalue())
                        temp_path = tmp.name
                    try:
                        image_notes = analyze_image(temp_path, engine, "chalkboard" if photo_purpose.startswith("Handwritten") else "scene")
                    except Exception as exc:
                        image_error = "Image analysis unavailable: " + str(exc)
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
                st.write("**Image observations (verify before use):**", image_notes)
            if image_error:
                st.warning(image_error + ". The text report was saved without image observations.")
            st.caption("Analysis method: " + record.get("ai_method", "unknown"))
            st.session_state["saved_notice"] = "Report saved locally as incident #" + str(incident_id)
            st.rerun()

with tab2:
    st.subheader("Incident command board")
    st.caption("Review urgent reports, search locations, and export the incident register.")
    demo_col, refresh_col = st.columns([3, 1])
    with demo_col:
        if st.button("＋ Load 3 demo incidents", help="Adds clearly labelled sample records for your presentation demo."):
            samples = [
                {"reporter":"DEMO-01","location":"Ravi River — Demo Sector","language":"Urdu","report":"DEMO DATA: Flood water is rising near 12 homes. Two elderly residents need evacuation support.","priority":"CRITICAL","summary":"DEMO: Rising flood water near homes; vulnerable residents may need urgent assistance.","recommended_action":"Verify water level and contact the local response team immediately.","signals":["flood","evacuation","vulnerable_people"],"ai_method":"demo_sample"},
                {"reporter":"DEMO-02","location":"Main Link Road — Demo Sector","language":"English","report":"DEMO DATA: A fallen tree and debris are blocking the road used by relief vehicles.","priority":"HIGH","summary":"DEMO: Road obstruction may delay relief vehicle access.","recommended_action":"Confirm alternate access route with field responders.","signals":["road_blockage","access"],"ai_method":"demo_sample"},
                {"reporter":"DEMO-03","location":"Community School — Demo Sector","language":"Punjabi","report":"DEMO DATA: Clean drinking water and blankets are needed for families at the temporary shelter.","priority":"MEDIUM","summary":"DEMO: Shelter requests drinking water and blankets.","recommended_action":"Confirm stock and coordinate a supply drop.","signals":["shelter","water","supplies"],"ai_method":"demo_sample"}
            ]
            for sample in samples:
                add_incident(sample)
            st.session_state["saved_notice"] = "3 demo incidents added. These are sample records, not live emergency reports."
            st.rerun()
    with refresh_col:
        if st.button("↻ Refresh board"):
            st.rerun()
    if incidents:
        df = pd.DataFrame(incidents)
        f1, f2 = st.columns([2, 1])
        search_term = f1.text_input("Search by location or summary", placeholder="e.g. flood, school, road")
        priority_filter = f2.selectbox("Priority filter", ["All", "CRITICAL", "HIGH", "MEDIUM", "LOW"])
        if search_term:
            mask = (df["location"].fillna("").str.contains(search_term, case=False) |
                    df["summary"].fillna("").str.contains(search_term, case=False))
            df = df[mask]
        if priority_filter != "All":
            df = df[df["priority"] == priority_filter]
        if not df.empty:
            st.dataframe(df[["id", "created_at", "location", "language", "priority", "summary", "status", "ai_method"]],
                         use_container_width=True, hide_index=True)
        else:
            st.info("No incidents match these filters.")
        st.download_button("Export CSV", df.to_csv(index=False).encode("utf-8"),
                           "relieflens_incidents.csv", "text/csv")
        st.download_button("Export JSON", json.dumps(incidents, ensure_ascii=False, indent=2),
                           "relieflens_incidents.json", "application/json")
    else:
        st.info("No reports yet. Submit a field report or load clearly labelled demo incidents for your presentation.")

with tab3:
    st.subheader("System integrations")
    st.markdown("""
| Track | Status in this starter build |
|---|---|
| Local Gemma 4 | Ollama adapter for text and images; local model must be installed |
| Gemini API Gemma 4 | Hosted text and image adapter; API key + internet required |
| Offline incident store | SQLite |
| Multilingual reports | Original text passed to model; no forced translation |
| Voice transcription | Optional local faster-whisper CPU add-on; install requirements-audio.txt |
| Handwritten chart extraction | Gemma 4 image prompt for legible transcription; human verification required |
| Snowflake CoCo | CoCo prompts and adaptable SQL templates committed; live account query pending |
| Solana Agent Registry | Draft metadata and safe registration guide; on-chain registration pending |
| Copilot evidence | Must be captured from actual Copilot use |
""")
    st.code("ollama pull gemma4:e2b\npip install -r requirements-audio.txt\nstreamlit run app.py", language="bash")
    st.info("Hosted mode: configure GEMINI_API_KEY in .env or your hosting provider secrets. Local mode requires Ollama and a downloaded Gemma model.")

st.divider()
st.caption("ReliefLens • Prototype for humanitarian coordination • Verify every alert with human responders.")
