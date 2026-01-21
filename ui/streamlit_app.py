# ui/streamlit_app.py

import sys
import io
from pathlib import Path
import streamlit as st
import plotly.graph_objects as go
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes

# --- Setup ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.ai_recruiter_evaluator import evaluate_resume_with_ai

st.set_page_config(page_title="AI Recruiter Pro", page_icon="🚀", layout="wide")

# --- Custom Styles ---
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
    </style>
""", unsafe_allow_html=True)

# --- PDF Processing (OCR + Layout) ---
def extract_text_from_pdf(file):
    text = ""
    try:
        file_bytes = file.read()
        if not file_bytes:
            return None 
            
        # Fast extraction (preserves columns/tables)
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text(layout=True)
                if extracted:
                    text += extracted + "\n"
        
        # Fallback to OCR if text is missing (scanned PDFs)
        if len(text.strip()) < 50:
            try:
                images = convert_from_bytes(file_bytes)
                ocr_text = ""
                for img in images:
                    ocr_text += pytesseract.image_to_string(img)
                text = ocr_text
            except:
                pass 
                
    except Exception:
        return None

    return text

# --- File Reading & Safety Checks ---
def read_input(file_upload, text_input):
    if file_upload:
        try:
            if file_upload.type == "application/pdf":
                content = extract_text_from_pdf(file_upload)
                return content if content else ""
            return file_upload.read().decode("utf-8", errors="ignore")
        except:
            return ""
    if text_input:
        return text_input.strip()
    return None

def validate_uploads(resume_text, jd_text):
    # 1. Safety: Check for empty/corrupted files
    if not resume_text or len(resume_text) < 50:
        return False, "⚠️ The Resume file looks empty or unreadable. Please check the file."
    if not jd_text or len(jd_text) < 50:
        return False, "⚠️ The Job Description looks empty or too short."

    # Convert to lower for case-insensitive matching
    r_lower = resume_text.lower()
    
    # 2. Strict Check: Must have at least one 'Resume' keyword
    # This blocks random files like recipes or lyrics
    resume_indicators = ["experience", "education", "skills", "projects", "summary", "profile", "contact", "work history"]
    if not any(ind in r_lower for ind in resume_indicators):
        return False, "⚠️ The uploaded file doesn't look like a valid resume. (Missing common keywords like 'Experience' or 'Skills')"

    # 3. Swap Check: Did they put the JD in the Resume slot?
    jd_indicators = ["job description", "about the role", "responsibilities", "requirements"]
    
    # If it screams 'JD' but whispers 'Resume', it's a swap
    has_jd_title = any(ind in r_lower[:200] for ind in jd_indicators)
    has_resume_content = any(ind in r_lower for ind in resume_indicators)
    
    if has_jd_title and not has_resume_content:
        return False, "⚠️ It looks like you uploaded a Job Description in the 'Resume' slot."

    return True, "Valid"

# --- Gauge Chart Component ---
def create_gauge_chart(score):
    if score >= 75:
        bar_color = "#00CC96"
    elif score >= 50:
        bar_color = "#FFA15A"
    else:
        bar_color = "#EF553B"

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

# --- Session State ---
if "evaluation_result" not in st.session_state:
    st.session_state.evaluation_result = None

def reset_app():
    st.session_state.evaluation_result = None
    st.rerun()

# --- Sidebar ---
with st.sidebar:
    st.title("🚀 AI Recruiter Pro")
    st.markdown("---")
    st.markdown("### 🎯 How it Works")
    st.markdown("1. **Upload Resume** (PDF/TXT)")
    st.markdown("2. **Upload Job Description** (PDF/TXT)")
    st.markdown("3. **Get AI Feedback**")
    st.markdown("---")
    st.info("💡 **Pro Tip:** Ensure your resume highlights impact and metrics, not just responsibilities.")

# --- Main App UI ---
st.markdown("## 🤖 Intelligent Resume Screening System")
st.divider()

if not st.session_state.evaluation_result:
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1️⃣ Candidate Resume")
        resume_tab_file, resume_tab_text = st.tabs(["📂 Upload File", "✍️ Paste Text"])
        with resume_tab_file:
            resume_file = st.file_uploader("Upload Resume (PDF/TXT)", type=["txt", "pdf"], key="res_file")
        with resume_tab_text:
            resume_text = st.text_area("Paste Resume Content", height=300, key="res_text")

    with col2:
        st.subheader("2️⃣ Job Description")
        jd_tab_file, jd_tab_text = st.tabs(["📂 Upload File", "✍️ Paste Text"])
        with jd_tab_file:
            jd_file = st.file_uploader("Upload JD (PDF/TXT)", type=["txt", "pdf"], key="jd_file")
        with jd_tab_text:
            jd_text = st.text_area("Paste JD Content", height=300, key="jd_text")

    st.markdown("---")
    
    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        analyze_btn = st.button("🔍 Analyze Profile Match", type="primary", use_container_width=True)

    if analyze_btn:
        # Read files safely
        resume_content = read_input(resume_file, resume_text)
        jd_content = read_input(jd_file, jd_text)

        # Basic Check
        if not resume_content or not jd_content:
            st.error("⚠️ Please upload BOTH a Resume and a Job Description.")
        else:
            # Deep Validation
            is_valid, error_msg = validate_uploads(resume_content, jd_content)
            
            if not is_valid:
                st.warning(error_msg)
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

# --- Results Dashboard ---
else:
    res = st.session_state.evaluation_result
    score = res.get("ats_score", 0)
    decision = res.get("decision", "BORDERLINE")

    col_chart, col_decision = st.columns([1, 1.5])
    
    with col_chart:
        st.plotly_chart(create_gauge_chart(score), use_container_width=True)
    
    with col_decision:
        st.write("") 
        st.write("") 
        if decision == "PASS":
            st.success(f"## ✅ Decision: PASS")
            st.markdown("**Recommendation:** Strong Hire.")
        elif decision == "BORDERLINE":
            st.warning(f"## ⚠️ Decision: BORDERLINE")
            st.markdown("**Recommendation:** Interview.")
        else:
            st.error(f"## ⛔ Decision: REJECT")
            st.markdown("**Recommendation:** Do Not Proceed.")
        
        st.markdown(f"**Executive Summary:** {res['decision_summary']}")
        st.button("🔄 Start New Analysis", on_click=reset_app)

    st.divider()

    tabs = st.tabs(["📊 Detailed Analysis", "💪 Strengths", "🚩 Gaps", "💡 Coaching Tips", "🔑 Keywords"])

    with tabs[0]: 
        st.write(res["detailed_explanation"])

    with tabs[1]: # Strengths with details
        for s in res["strengths"]:
            with st.expander(f"**{s['title']}**", expanded=True):
                st.success(f"**Resume Evidence:** {s['resume_reference']}")
                st.caption(f"JD Requirement: {s.get('jd_reference', 'N/A')}")
                st.write(s['explanation'])

    with tabs[2]: # Gaps with comparison columns
        for g in res["gaps"]:
            with st.container():
                st.error(f"**Gap: {g['title']}**")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Expected:** {g.get('jd_reference', 'N/A')}")
                with c2:
                    st.markdown(f"**Found:** {g.get('resume_reference', 'N/A')}")
                
                st.markdown(f"*Impact: {g['impact']}*")
                st.divider()

    with tabs[3]: # Coaching with context
        for i in res["improvement_suggestions"]:
            with st.container():
                st.info(f"👉 **{i['suggestion_title']}**")
                st.write(f"**Advice:** {i['suggestion']}")
                st.caption(f"Context: {i.get('note', '')}")

    with tabs[4]: # Keywords with pills
        ka = res["keyword_analysis"]
        st.markdown("**Matched:** " + " ".join([f'<span class="keyword-pill">✓ {k}</span>' for k in ka['clearly_present_in_resume']]), unsafe_allow_html=True)
        st.markdown("<br>**Missing:** " + " ".join([f'<span class="missing-pill">✗ {k}</span>' for k in ka['missing_from_resume']]), unsafe_allow_html=True)
