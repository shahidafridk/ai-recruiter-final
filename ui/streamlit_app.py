# ui/streamlit_app.py

import sys
from pathlib import Path
import streamlit as st
import plotly.graph_objects as go

# ----------------
# SETUP & CONFIG
# ---------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.ai_recruiter_evaluator import evaluate_resume_with_ai

st.set_page_config(page_title="AI Recruiter Pro", page_icon="🚀", layout="wide")

# --------------------------------
# CUSTOM CSS (Dark Mode Friendly)
# -------------------------------
st.markdown("""
    <style>
    .metric-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #41424C;
        text-align: center;
    }
    .keyword-pill {
        display: inline-block;
        padding: 5px 10px;
        background-color: #0E1117;
        color: #00FF00;
        border: 1px solid #00FF00;
        border-radius: 15px;
        margin: 2px;
        font-size: 0.8em;
        font-weight: 600;
    }
    .missing-pill {
        display: inline-block;
        padding: 5px 10px;
        background-color: #0E1117;
        color: #FF4B4B;
        border: 1px solid #FF4B4B;
        border-radius: 15px;
        margin: 2px;
        font-size: 0.8em;
        font-weight: 600;
    }
    .weak-pill {
        display: inline-block;
        padding: 5px 10px;
        background-color: #0E1117;
        color: #FFA500;
        border: 1px solid #FFA500;
        border-radius: 15px;
        margin: 2px;
        font-size: 0.8em;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------
# HELPER: FILE READER
# --------------------
def read_input(file_upload, text_input):
    if file_upload:
        return file_upload.read().decode("utf-8", errors="ignore")
    if text_input:
        return text_input.strip()
    return None

# ----------------------------
# HELPER: DYNAMIC GAUGE CHART
# ---------------------------
def create_gauge_chart(score):
    if score >= 75:
        bar_color = "#00CC96"  # Green
    elif score >= 50:
        bar_color = "#FFA15A"  # Orange
    else:
        bar_color = "#EF553B"  # Red

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': "ATS Score", 'font': {'size': 24, 'color': "white"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': bar_color},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "#333",
            'steps': [
                {'range': [0, 50], 'color': 'rgba(239, 85, 59, 0.2)'},
                {'range': [50, 75], 'color': 'rgba(255, 161, 90, 0.2)'},
                {'range': [75, 100], 'color': 'rgba(0, 204, 150, 0.2)'}
            ],
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", 
        font={'color': "white", 'family': "Arial"},
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

# ----------------
# STATE MANAGEMENT
# ----------------
if "evaluation_result" not in st.session_state:
    st.session_state.evaluation_result = None

def reset_app():
    st.session_state.evaluation_result = None
    st.rerun()

# ---------
# SIDEBAR
# ---------
with st.sidebar:
    st.title("🚀 AI Recruiter Pro")
    st.markdown("---")
    st.markdown("### 🎯 How it Works")
    st.markdown("1. **Upload Resume** (TXT)")
    st.markdown("2. **Upload Job Description** (TXT)")
    st.markdown("3. **Get AI Feedback**")
    st.markdown("---")
    st.info("💡 **Pro Tip:** Ensure your resume highlights impact and metrics, not just responsibilities.")

# ---------
# MAIN UI
# ---------
st.markdown("## 🤖 Intelligent Resume Screening System")
st.markdown("Simulate a Senior Technical Recruiter evaluation in seconds.")
st.divider()

# --- INPUT SECTION ---
if not st.session_state.evaluation_result:
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1️⃣ Candidate Resume")
        resume_tab_file, resume_tab_text = st.tabs(["📂 Upload File", "✍️ Paste Text"])
        
        with resume_tab_file:
            resume_file = st.file_uploader("Upload Resume (TXT)", type=["txt"], key="res_file")
        with resume_tab_text:
            resume_text = st.text_area("Paste Resume Content", height=300, key="res_text")

    with col2:
        st.subheader("2️⃣ Job Description")
        jd_tab_file, jd_tab_text = st.tabs(["📂 Upload File", "✍️ Paste Text"])
        
        with jd_tab_file:
            jd_file = st.file_uploader("Upload JD (TXT)", type=["txt"], key="jd_file")
        with jd_tab_text:
            jd_text = st.text_area("Paste JD Content", height=300, key="jd_text")

    st.markdown("---")
    
    # Analyze Button
    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        analyze_btn = st.button("🔍 Analyze Profile Match", type="primary", use_container_width=True)

    if analyze_btn:
        resume_content = read_input(resume_file, resume_text)
        jd_content = read_input(jd_file, jd_text)

        if not resume_content or not jd_content:
            st.error("⚠️ Please provide BOTH a Resume and a Job Description.")
        else:
            with st.spinner("🤖 Analyzing credentials against requirements..."):
                try:
                    raw_result = evaluate_resume_with_ai(
                        resume_text=resume_content,
                        job_description_text=jd_content,
                    )
                    st.session_state.evaluation_result = raw_result
                    st.rerun()
                except Exception as e:
                    st.error(f"System Error: {str(e)}")

# --- RESULTS DASHBOARD ---
else:
    res = st.session_state.evaluation_result
    score = res.get("ats_score", 0)
    decision = res.get("decision", "BORDERLINE")

    # Header Stats
    col_chart, col_decision = st.columns([1, 1.5])
    
    with col_chart:
        st.plotly_chart(create_gauge_chart(score), use_container_width=True)
    
    with col_decision:
        st.write("") # Spacer
        st.write("") # Spacer
        
        # --- DISPLAY BOTH DECISION AND RECOMMENDATION ---
        if decision == "PASS":
            st.success(f"## ✅ Decision: PASS")
            st.markdown("**Recommendation:** Strong Hire. Candidate meets core requirements.")
        elif decision == "BORDERLINE":
            st.warning(f"## ⚠️ Decision: BORDERLINE")
            st.markdown("**Recommendation:** Interview. Probe specifically on identified gaps.")
        else:
            st.error(f"## ⛔ Decision: REJECT")
            st.markdown("**Recommendation:** Do Not Proceed. Significant skill mismatch.")
        
        st.markdown(f"**Executive Summary:** {res['decision_summary']}")
        st.button("🔄 Start New Analysis", on_click=reset_app)

    st.divider()

    # Detailed Tabs
    tabs = st.tabs(["📊 Detailed Analysis", "💪 Strengths", "🚩 Gaps", "💡 Coaching Tips", "🔑 Keywords"])

    with tabs[0]: # Analysis
        st.markdown("### Executive Explanation")
        st.write(res["detailed_explanation"])

    with tabs[1]: # Strengths
        st.markdown("### ✅ Matching Qualifications")
        if not res["strengths"]:
            st.info("No specific strong matches found.")
        for s in res["strengths"]:
            with st.expander(f"**{s['title']}**", expanded=True):
                st.success(f"**Resume Evidence:** {s['resume_reference']}")
                st.caption(f"JD Requirement: {s['jd_reference']}")
                st.write(s['explanation'])

    with tabs[2]: # Gaps
        st.markdown("### ⚠️ Critical Missing Requirements")
        if not res["gaps"]:
            st.success("No critical gaps found.")
        for g in res["gaps"]:
            with st.container():
                st.error(f"**Gap: {g['title']}**")
                c1, c2 = st.columns(2)
                c1.markdown(f"**Expected:** {g['jd_reference']}")
                c2.markdown(f"**Found:** {g['resume_reference']}")
                st.markdown(f"*Impact: {g['impact']}*")
                st.divider()

    with tabs[3]: # Improvements
        st.markdown("### 🚀 Career Coaching & Feedback")
        for i in res["improvement_suggestions"]:
            with st.container():
                st.info(f"👉 **{i['suggestion_title']}**")
                st.write(f"**Advice:** {i['suggestion']}")
                st.caption(f"Context: {i['note']}")

    with tabs[4]: # Keywords
        st.markdown("### 🔑 Keyword Scan")
        ka = res["keyword_analysis"]
        
        st.markdown("**Matched Keywords:**")
        if ka['clearly_present_in_resume']:
            st.markdown(" ".join([f'<span class="keyword-pill">✓ {k}</span>' for k in ka['clearly_present_in_resume']]), unsafe_allow_html=True)
        else:
            st.write("No direct keyword matches.")

        st.markdown("<br>**Missing Keywords:**", unsafe_allow_html=True)
        if ka['missing_from_resume']:
            st.markdown(" ".join([f'<span class="missing-pill">✗ {k}</span>' for k in ka['missing_from_resume']]), unsafe_allow_html=True)
        else:
            st.write("No missing keywords detected.")
            
        st.markdown("<br>**Weak/Implicit Keywords:**", unsafe_allow_html=True)
        if ka['weak_or_implicit_in_resume']:
            st.markdown(" ".join([f'<span class="weak-pill">~ {k}</span>' for k in ka['weak_or_implicit_in_resume']]), unsafe_allow_html=True)
        else:

            st.write("None.")
