import json
import os
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from relieflens.audio import transcribe_audio
from relieflens.database import add_incident, init_db, list_incidents, update_incident_status
from relieflens.gemma import analyze_image, analyze_text
from relieflens.triage import triage_text

load_dotenv()
st.set_page_config(page_title="ReliefLens | Disaster Coordination", page_icon="🆘", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@500;600;700;800&display=swap');
:root{--ink:#14283d;--muted:#64788b;--teal:#087f78;--teal2:#0fa99a;--line:#dce6ed;--surface:#ffffff;--canvas:#f3f7fa;}
.stApp{background:var(--canvas);color:var(--ink);font-family:'DM Sans',sans-serif}
[data-testid="stHeader"]{background:rgba(243,247,250,.88)}
.block-container{max-width:1480px;padding:1.6rem 2.1rem 3rem}
h1,h2,h3{font-family:'Manrope','DM Sans',sans-serif;color:var(--ink)!important;letter-spacing:-.035em}
h1{font-size:2.35rem!important;font-weight:800!important}
h2{font-size:1.55rem!important;font-weight:800!important}
h3{font-size:1.12rem!important;font-weight:750!important}
p,label,.stMarkdown{color:#42586b}
[data-testid="stCaptionContainer"] p,.stCaption{color:#71869a!important}
[data-testid="stMetric"]{background:var(--surface);border:1px solid var(--line);border-radius:17px;padding:18px 20px;box-shadow:0 5px 18px rgba(22,48,69,.045)}
[data-testid="stMetricLabel"]{color:#6c8193;font-weight:700;font-size:.83rem}
[data-testid="stMetricValue"]{color:#087f78;font-weight:800;font-family:'Manrope',sans-serif}
[data-testid="stMetricDelta"]{color:#168575}
.stTabs [data-baseweb="tab-list"]{gap:8px;border-bottom:1px solid var(--line);background:#eaf0f4;padding:7px;border-radius:14px}
.stTabs [data-baseweb="tab"]{height:43px;padding:0 17px;border-radius:10px;color:#607488;font-weight:750}
.stTabs [aria-selected="true"]{background:#fff!important;color:#087f78!important;box-shadow:0 2px 8px rgba(20,40,61,.08)}
input,textarea,[data-baseweb="select"]>div{background:#fff!important;border-color:#d5e0e8!important;border-radius:10px!important;color:#193149!important}
[data-testid="stFileUploader"] section{background:#f8fbfd;border:1px dashed #9bb5c3;border-radius:14px}
div.stButton>button,div.stDownloadButton>button,div.stFormSubmitButton>button{border-radius:10px;min-height:42px;font-weight:750;border:1px solid #cbd9e2;background:#fff;color:#29445a;transition:all .15s ease}
div.stButton>button[kind="primary"],div.stFormSubmitButton>button[kind="primary"]{background:linear-gradient(105deg,#087f78,#10a99a);border:0;color:white;box-shadow:0 5px 14px rgba(8,127,120,.17)}
div.stButton>button:hover,div.stDownloadButton>button:hover{border-color:#0fa99a;color:#087f78;transform:translateY(-1px)}
[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:13px;overflow:hidden;background:white}
[data-testid="stAlert"]{border-radius:12px;border:1px solid var(--line)}
[data-testid="stExpander"]{background:#fff;border:1px solid var(--line);border-radius:13px;overflow:hidden}
[data-testid="stExpander"] summary{font-weight:700;color:#203b50}
[data-testid="stForm"]{background:#fff;border:1px solid var(--line);border-radius:18px;padding:20px 22px;box-shadow:0 5px 20px rgba(22,48,69,.04)}
[data-testid="stRadio"] label{font-weight:600}
hr{border-color:var(--line)}
</style>
""", unsafe_allow_html=True)
init_db()
st.markdown("""
<div style="position:relative;overflow:hidden;background:linear-gradient(115deg,#102c42 0%,#16475a 58%,#087f78 100%);border:1px solid rgba(255,255,255,.13);border-radius:23px;padding:30px 34px;margin:5px 0 22px;box-shadow:0 15px 35px rgba(17,48,68,.13)">
  <div style="position:absolute;right:-35px;top:-95px;width:300px;height:300px;border:1px solid rgba(255,255,255,.12);border-radius:50%;box-shadow:0 0 0 34px rgba(255,255,255,.035),0 0 0 70px rgba(255,255,255,.025)"></div>
  <div style="position:relative;display:flex;align-items:center;gap:11px;margin-bottom:12px">
    <span style="font-size:29px">🆘</span><span style="font-family:Manrope,sans-serif;font-size:30px;font-weight:800;letter-spacing:-1.2px;color:#fff">ReliefLens</span>
    <span style="margin-left:7px;padding:6px 11px;border:1px solid rgba(125,242,218,.3);border-radius:30px;background:rgba(125,242,218,.12);color:#9af3df;font-size:10px;font-weight:800;letter-spacing:1.3px">RESPONSE COMMAND</span>
  </div>
  <div style="position:relative;font-family:Manrope,sans-serif;font-size:23px;font-weight:800;letter-spacing:-.6px;color:#fff;margin-bottom:7px">See the signal. Prioritize the response.</div>
  <div style="position:relative;font-size:14px;line-height:1.7;color:#d1e4e9;max-width:850px">A field coordination workspace that turns multilingual reports, voice notes and scene images into organized incidents for human review.</div>
  <div style="position:relative;display:flex;gap:9px;flex-wrap:wrap;margin-top:19px"><span style="padding:6px 10px;border-radius:8px;background:rgba(255,255,255,.1);color:#e9f7f7;font-size:11px;font-weight:700">● Offline-first storage</span><span style="padding:6px 10px;border-radius:8px;background:rgba(255,255,255,.1);color:#e9f7f7;font-size:11px;font-weight:700">● Multilingual intake</span><span style="padding:6px 10px;border-radius:8px;background:rgba(255,255,255,.1);color:#e9f7f7;font-size:11px;font-weight:700">● Human-verified triage</span></div>
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
    st.caption("Filter incoming reports, inspect field details, and track response progress.")
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
        m1, m2, m3 = st.columns(3)
        m1.metric("Awaiting response", int((df["status"] == "OPEN").sum()))
        m2.metric("Teams working", int((df["status"] == "IN_PROGRESS").sum()))
        m3.metric("Resolved", int((df["status"] == "RESOLVED").sum()))

        with st.expander("📊 Priority overview", expanded=False):
            priority_counts = (df["priority"].value_counts()
                               .reindex(["CRITICAL", "HIGH", "MEDIUM", "LOW"], fill_value=0))
            st.bar_chart(priority_counts, horizontal=True, height=190)

        f1, f2, f3 = st.columns([2, 1, 1])
        search_term = f1.text_input("Search incidents", placeholder="Location, report, signal...")
        priority_filter = f2.selectbox("Priority", ["All", "CRITICAL", "HIGH", "MEDIUM", "LOW"])
        status_filter = f3.selectbox("Response status", ["All", "OPEN", "IN_PROGRESS", "RESOLVED"])
        filtered = df.copy()
        if search_term:
            mask = (
                filtered["location"].fillna("").str.contains(search_term, case=False, na=False) |
                filtered["summary"].fillna("").str.contains(search_term, case=False, na=False) |
                filtered["report"].fillna("").str.contains(search_term, case=False, na=False)
            )
            filtered = filtered[mask]
        if priority_filter != "All":
            filtered = filtered[filtered["priority"] == priority_filter]
        if status_filter != "All":
            filtered = filtered[filtered["status"] == status_filter]

        st.caption(f"Showing {len(filtered)} of {len(df)} incidents • Highest priority first")
        if not filtered.empty:
            st.dataframe(
                filtered[["id", "created_at", "location", "language", "priority", "summary", "status", "ai_method"]],
                use_container_width=True, hide_index=True
            )
            st.markdown("#### Incident details & response tracking")
            for _, incident in filtered.iterrows():
                priority = str(incident.get("priority", "LOW"))
                icon = {"CRITICAL":"🔴", "HIGH":"🟠", "MEDIUM":"🟡", "LOW":"🟢"}.get(priority, "⚪")
                title = f"{icon} #{incident['id']} · {incident['location']} · {priority}"
                with st.expander(title):
                    left, right = st.columns([2, 1])
                    with left:
                        st.write("**Summary**")
                        st.write(incident.get("summary") or "No summary available.")
                        st.write("**Original field report**")
                        st.write(incident.get("report") or "No report text.")
                        st.write("**Recommended next step**")
                        st.write(incident.get("recommended_action") or "Human review required.")
                        signals = incident.get("signals_json", "[]")
                        try:
                            parsed_signals = json.loads(signals) if isinstance(signals, str) else signals
                        except (TypeError, ValueError):
                            parsed_signals = []
                        st.caption("Signals: " + (", ".join(parsed_signals) if parsed_signals else "None recorded"))
                    with right:
                        st.caption(f"Reporter: {incident.get('reporter') or 'Not provided'}")
                        st.caption(f"Language: {incident.get('language') or 'Unknown'}")
                        st.caption(f"Analysis: {incident.get('ai_method') or 'Unknown'}")
                        current_status = str(incident.get("status", "OPEN"))
                        new_status = st.selectbox(
                            "Update response status",
                            ["OPEN", "IN_PROGRESS", "RESOLVED"],
                            index=["OPEN", "IN_PROGRESS", "RESOLVED"].index(current_status)
                                if current_status in ["OPEN", "IN_PROGRESS", "RESOLVED"] else 0,
                            key=f"status_{incident['id']}"
                        )
                        if new_status != current_status and st.button(
                            "Save status", key=f"save_status_{incident['id']}", type="primary"
                        ):
                            update_incident_status(int(incident["id"]), new_status)
                            st.session_state["saved_notice"] = f"Incident #{incident['id']} status updated to {new_status}."
                            st.rerun()
        else:
            st.info("No incidents match these filters.")

        export_col1, export_col2 = st.columns(2)
        export_col1.download_button(
            "⬇ Export filtered CSV", filtered.to_csv(index=False).encode("utf-8"),
            "relieflens_incidents_filtered.csv", "text/csv", use_container_width=True
        )
        export_col2.download_button(
            "⬇ Export all incidents (JSON)",
            json.dumps(incidents, ensure_ascii=False, indent=2),
            "relieflens_incidents.json", "application/json", use_container_width=True
        )
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
