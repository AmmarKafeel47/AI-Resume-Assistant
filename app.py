import streamlit as st
import re
import html as html_lib
from modules.parser import ResumeParser
from modules.resume_analyzer import ResumeAnalyzer
from modules.jd_analyzer import JDAnalyzer
from modules.matcher import ResumeMatcher
from modules.recommendation_engine import RecommendationEngine
from modules.resume_generator import ResumeGenerator
from modules.exporter import Exporter
from modules.docx_exporter import DocxExporter
from modules.cover_letter_generator import CoverLetterGenerator
from modules.cover_letter_exporter import CoverLetterExporter

# ============================================================
# Page Configuration/Below the CSS, add these helper functions:
# ============================================================
st.set_page_config(
    page_title="ResumePilot AI",
    page_icon="📄",
    layout="wide"
)

# ============================================================
# UI Styling
# ============================================================
st.markdown("""
<style>

/* =========================================================
   Navy Theme
========================================================= */

:root {
    --app-bg: #0b1120;
    --app-bg-dark: #020617;

    --card-bg: #111827;
    --card-bg-2: #172033;
    --card-border: #2f3b52;

    --text-main: #f8fafc;
    --text-muted: #94a3b8;
    --text-soft: #cbd5e1;

    --primary: #38bdf8;

    --success-bg: #064e3b;
    --success-text: #a7f3d0;

    --warning-bg: #78350f;
    --warning-text: #fde68a;

    --danger-bg: #7f1d1d;
    --danger-text: #fecaca;

    --pill-match-bg: #1e3a8a;
    --pill-match-text: #dbeafe;

    --pill-missing-bg: #7f1d1d;
    --pill-missing-text: #fecaca;
}

/* =========================================================
   App Background
========================================================= */

.stApp {
    background: linear-gradient(180deg, var(--app-bg) 0%, var(--app-bg-dark) 100%) !important;
    color: var(--text-main) !important;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

/* =========================================================
   Text
========================================================= */

h1, h2, h3, h4, h5, h6 {
    color: var(--text-main) !important;
    font-weight: 750 !important;
}

p {
    color: var(--text-soft) !important;
    line-height: 1.65 !important;
}

/* =========================================================
   Hero - Animated Premium Header
========================================================= */

.hero-card {
    position: relative;
    overflow: hidden;
    background:
        radial-gradient(circle at 15% 15%, rgba(56, 189, 248, 0.22), transparent 32%),
        radial-gradient(circle at 85% 20%, rgba(99, 102, 241, 0.22), transparent 34%),
        linear-gradient(135deg, #111827 0%, #172033 55%, #0b1120 100%);
    border: 1px solid rgba(148, 163, 184, 0.25);
    border-radius: 28px;
    padding: 54px 58px;
    margin-bottom: 34px;
    box-shadow:
        0 20px 55px rgba(0, 0, 0, 0.35),
        inset 0 0 35px rgba(255, 255, 255, 0.03);
    animation: heroFloat 5s ease-in-out infinite;
}

.hero-card::before {
    content: "";
    position: absolute;
    width: 420px;
    height: 420px;
    top: -180px;
    right: -120px;
    background: radial-gradient(circle, rgba(56, 189, 248, 0.32), transparent 65%);
    filter: blur(10px);
    animation: heroGlow 7s ease-in-out infinite alternate;
}

.hero-card::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(
        120deg,
        transparent 0%,
        rgba(255, 255, 255, 0.08) 45%,
        transparent 65%
    );
    transform: translateX(-100%);
    animation: heroShine 5.5s ease-in-out infinite;
}

.hero-content {
    position: relative;
    z-index: 2;
}

.hero-badge {
    display: inline-block;
    padding: 8px 15px;
    margin-bottom: 20px;
    border-radius: 999px;
    background: rgba(30, 58, 138, 0.55);
    border: 1px solid rgba(147, 197, 253, 0.28);
    color: #bfdbfe;
    font-size: 14px;
    font-weight: 750;
    letter-spacing: 0.2px;
}

.hero-title {
    font-size: 58px;
    line-height: 1.05;
    font-weight: 900;
    letter-spacing: -2px;
    margin: 0 0 18px 0;
    background: linear-gradient(90deg, #ffffff, #bfdbfe, #38bdf8, #ffffff);
    background-size: 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: titleGradient 4s ease-in-out infinite;
}

.hero-subtitle {
    color: var(--text-muted) !important;
    font-size: 20px;
    line-height: 1.65;
    max-width: 920px;
    margin: 0;
}

.hero-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 30px;
}

.hero-pill {
    padding: 10px 15px;
    border-radius: 999px;
    background: rgba(15, 23, 42, 0.72);
    border: 1px solid rgba(148, 163, 184, 0.25);
    color: #e5e7eb;
    font-size: 14px;
    font-weight: 700;
    transition: all 0.25s ease;
}

.hero-pill:hover {
    transform: translateY(-4px);
    border-color: rgba(56, 189, 248, 0.75);
    box-shadow: 0 12px 28px rgba(56, 189, 248, 0.18);
}

@keyframes heroFloat {
    0%, 100% {
        transform: translateY(0);
    }
    50% {
        transform: translateY(-5px);
    }
}

@keyframes heroGlow {
    from {
        transform: translate(0, 0) scale(1);
    }
    to {
        transform: translate(-80px, 70px) scale(1.15);
    }
}

@keyframes heroShine {
    0% {
        transform: translateX(-100%);
    }
    45%, 100% {
        transform: translateX(100%);
    }
}

@keyframes titleGradient {
    0% {
        background-position: 0%;
    }
    50% {
        background-position: 100%;
    }
    100% {
        background-position: 0%;
    }
}

@media (max-width: 768px) {
    .hero-card {
        padding: 38px 28px;
        border-radius: 24px;
    }

    .hero-title {
        font-size: 42px;
    }

    .hero-subtitle {
        font-size: 17px;
    }
}


/* =========================================================
   Cards
========================================================= */

.metric-card,
.section-card,
.coach-card,
.download-card,
.status-card,
.insight-card {
    background: linear-gradient(180deg, var(--card-bg) 0%, var(--card-bg-2) 100%) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 20px !important;
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.24) !important;
    color: var(--text-main) !important;
}

.section-card,
.coach-card,
.download-card,
.status-card,
.insight-card {
    padding: 26px 28px !important;
    margin-bottom: 24px !important;
}

.section-card h3,
.coach-card h3,
.download-card h3,
.status-card h3,
.insight-card h3 {
    color: var(--text-main) !important;
    font-size: 24px !important;
    font-weight: 750 !important;
    margin-bottom: 18px !important;
}

.section-card p,
.coach-card p,
.download-card p,
.status-card p,
.insight-card p {
    color: var(--text-soft) !important;
    font-size: 16px !important;
    line-height: 1.65 !important;
}

/* =========================================================
   Metric Cards
========================================================= */

.metric-card {
    min-height: 130px !important;
    padding: 28px 24px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: center !important;
    text-align: center !important;
}

.metric-value {
    color: var(--text-main) !important;
    font-size: 34px !important;
    line-height: 1.1 !important;
    font-weight: 850 !important;
    margin-bottom: 10px !important;
    text-align: center !important;
}

.metric-label {
    color: var(--text-muted) !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    text-align: center !important;
}

/* =========================================================
   Match Status
========================================================= */

.status-card {
    min-height: 160px !important;
}

.status-card p {
    margin-top: 18px !important;
}

.status-pill {
    display: inline-block;
    padding: 7px 13px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 700;
}

.pill-green {
    background: var(--success-bg) !important;
    color: var(--success-text) !important;
}

.pill-yellow,
.pill-orange {
    background: var(--warning-bg) !important;
    color: var(--warning-text) !important;
}

.pill-red {
    background: var(--danger-bg) !important;
    color: var(--danger-text) !important;
}

/* =========================================================
   Skill Pills
========================================================= */

.skill-pill {
    display: inline-block !important;
    padding: 8px 14px !important;
    margin: 5px 6px 5px 0 !important;
    border-radius: 999px !important;
    font-size: 14px !important;
    font-weight: 650 !important;
    background: var(--pill-match-bg) !important;
    color: var(--pill-match-text) !important;
    border: 1px solid rgba(219, 234, 254, 0.18) !important;
}

.missing-pill {
    display: inline-block !important;
    padding: 8px 14px !important;
    margin: 5px 6px 5px 0 !important;
    border-radius: 999px !important;
    font-size: 14px !important;
    font-weight: 650 !important;
    background: var(--pill-missing-bg) !important;
    color: var(--pill-missing-text) !important;
    border: 1px solid rgba(254, 202, 202, 0.18) !important;
}

/* =========================================================
   Career Coach Items
========================================================= */

.gap-item {
    padding: 14px 0 !important;
    border-bottom: 1px solid rgba(148, 163, 184, 0.18) !important;
}

.gap-item:last-child {
    border-bottom: none !important;
}

.gap-title {
    color: var(--text-main) !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    margin-bottom: 6px !important;
}

.gap-text {
    color: var(--text-muted) !important;
    font-size: 15px !important;
    line-height: 1.55 !important;
}

/* =========================================================
   Boxes
========================================================= */

.success-box {
    background: rgba(6, 78, 59, 0.95) !important;
    color: var(--success-text) !important;
    border: 1px solid rgba(167, 243, 208, 0.3) !important;
    border-radius: 16px !important;
    padding: 16px 20px !important;
    margin-bottom: 18px !important;
}

.warning-box {
    background: rgba(120, 53, 15, 0.95) !important;
    color: var(--warning-text) !important;
    border: 1px solid rgba(253, 230, 138, 0.3) !important;
    border-radius: 16px !important;
    padding: 16px 20px !important;
    margin-bottom: 18px !important;
}

/* =========================================================
   Streamlit Components
========================================================= */

.stProgress > div > div > div > div {
    background-color: var(--primary) !important;
}

.stButton > button,
.stDownloadButton > button {
    background: #111827 !important;
    color: var(--text-main) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    border-color: var(--primary) !important;
    color: #ffffff !important;
}

div[data-testid="stExpander"] {
    background: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 14px !important;
}

div[data-testid="stExpander"] summary {
    color: var(--text-main) !important;
}

hr {
    border-color: #263244 !important;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# Reusable UI Helper Functions
# ============================================================

import html as html_lib


def safe_text(value):
    if value is None:
        return ""
    return html_lib.escape(str(value))


def render_hero():
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">ResumePilot AI</div>
            <p class="hero-subtitle">
                AI-powered resume tailoring, ATS analysis, and application package generation.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_metric_card(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{safe_text(value)}</div>
            <div class="metric-label">{safe_text(label)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def get_score_status(score):
    if score >= 85:
        return "Excellent Match", "pill-green"
    elif score >= 70:
        return "Good Match", "pill-yellow"
    elif score >= 50:
        return "Fair Match", "pill-orange"
    else:
        return "Low Match", "pill-red"


def render_skill_pills(skills, missing=False):
    if not skills:
        st.caption("None")
        return

    css_class = "missing-pill" if missing else "skill-pill"

    pills_html = "".join(
        f'<span class="{css_class}">{safe_text(skill)}</span>'
        for skill in skills
    )

    st.markdown(pills_html, unsafe_allow_html=True)


def html_skill_pills(skills, missing=False):
    if not skills:
        return "<p>No items available.</p>"

    css_class = "missing-pill" if missing else "skill-pill"

    return "".join(
        f'<span class="{css_class}">{safe_text(skill)}</span>'
        for skill in skills
    )


def render_summary_card(title, lines):
    lines_html = ""

    for line in lines:
        lines_html += f"<p>{safe_text(line)}</p>"

    st.markdown(
        f"""
        <div class="section-card">
            <h3>{safe_text(title)}</h3>
            {lines_html}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# Session State
# ============================================================

DEFAULT_STATE = {
    "resume_text": None,
    "resume_json": None,
    "jd_json": None,
    "match_result": None,
    "recommendations": None,
    "tailored_resume": None,
    "cover_letter": None
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value
        
        
        
# ============================================================
# Header
# ============================================================

render_hero()

# ============================================================
# Resume Upload
# ============================================================
st.subheader("📄 Upload Resume")

uploaded_file = st.file_uploader(
    "Upload your Resume (PDF or DOCX)",
    type=["pdf", "docx"]
)

if uploaded_file:
    st.success(f"✅ Resume uploaded: {uploaded_file.name}")
    
analyze_resume_button = st.button(
    "📄 Analyze Resume",
    use_container_width=True
)

resume_text = None


if analyze_resume_button:

    if uploaded_file is None:

        st.warning("Please upload a resume file first.")
    else:
        try:

            resume_text = ResumeParser.extract_text(uploaded_file)
  
            analyzer = ResumeAnalyzer()

            with st.spinner("Analyzing resume..."):
                st.session_state["resume_json"] = analyzer.analyze(resume_text)
                st.session_state["resume_text"] = resume_text
                
            st.success("✅ Resume analyzed successfully!")

        except Exception as e:

            st.error(e)
            

resume = st.session_state.get("resume_json")
resume_text = st.session_state.get("resume_text")

if resume:

    skills = resume.get("skills", {})

    total_skills = sum(
        len(value)
        for value in skills.values()
        if isinstance(value, list)
    )

    st.info(
        f"""
**Candidate:** {resume.get("personal_information", {}).get("name", "Unknown")}

• Skills Extracted: {total_skills}

• Experience Entries: {len(resume.get("experience", []))}

• Projects: {len(resume.get("projects", []))}

• Education: {len(resume.get("education", []))}
"""
    )

st.divider()


# ============================================================
# Job Description
# ============================================================
st.subheader("📋 Job Description")

job_description = st.text_area(
    "Paste the Job Description",
    height=250,
    placeholder="Paste the complete job description here..."
)

analyze_button = st.button(
    "🚀 Analyze Job Description",
    use_container_width=True
)


if analyze_button:

    if not job_description.strip():

        st.warning("Please paste a Job Description.")

    else:

        try:

            analyzer = JDAnalyzer()

            with st.spinner("Analyzing Job Description..."):

                st.session_state["jd_json"] = analyzer.analyze(
                    job_description
                )

            st.success("✅ Job Description analyzed successfully.")
            
        except Exception as e:

            st.error(f"AI Analysis Failed\n\n{e}")
            
            
jd = st.session_state.get("jd_json")

if jd:

    st.info(
        f"""
### 👔 Job Description Summary

**Job Title:** {jd.get("job_title", "Not detected")}

**Company:** {jd.get("company", "Not detected")}

• Skills Required: {len(jd.get("required_skills", []))}

• Responsibilities: {len(jd.get("responsibilities", []))}

• Qualifications: {len(jd.get("qualifications", []))}
"""
 )


st.divider()


# ============================================================
# Resume Matching
# ============================================================
st.subheader("🎯 Resume Matching")

generate_button = st.button(
    "🚀 Generate Application Package",
    use_container_width=True
)

if generate_button:

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    if st.session_state["resume_json"] is None:
        st.warning("Please analyze a resume first.")
        st.stop()

    if st.session_state["jd_json"] is None:
        st.warning("Please analyze a Job Description first.")
        st.stop()

    # --------------------------------------------------------
    # Resume Matching
    # --------------------------------------------------------

    with st.spinner("Matching resume against job description..."):

        matcher = ResumeMatcher(
            st.session_state["resume_json"],
            st.session_state["jd_json"]
        )

        st.session_state["match_result"] = matcher.match()

    # --------------------------------------------------------
    # AI Recommendations
    # --------------------------------------------------------

    with st.spinner("Generating AI recommendations..."):

        recommendation_engine = RecommendationEngine()

        st.session_state["recommendations"] = (
            recommendation_engine.generate(
                st.session_state["resume_json"],
                st.session_state["jd_json"],
                st.session_state["match_result"]
            )
        )

    # --------------------------------------------------------
    # Tailored Resume
    # --------------------------------------------------------

    with st.spinner("Generating tailored resume..."):

        generator = ResumeGenerator()

        tailored_resume = generator.generate(
            st.session_state["resume_json"],
            st.session_state["jd_json"],
            st.session_state["match_result"],
            st.session_state["recommendations"]
        )

    st.session_state["tailored_resume"] = tailored_resume

    # --------------------------------------------------------
    # Cover Letter
    # --------------------------------------------------------

    with st.spinner("Generating cover letter..."):

        cover_generator = CoverLetterGenerator()

        st.session_state["cover_letter"] = cover_generator.generate(
            st.session_state["resume_json"],
            st.session_state["tailored_resume"],
            st.session_state["jd_json"]
        )

    # --------------------------------------------------------
    # Save Analysis
    # --------------------------------------------------------

    saved_folder = Exporter.save_analysis(
        st.session_state["resume_json"],
        st.session_state["jd_json"],
        st.session_state["match_result"]
    )

    st.success("✅ Application package generated successfully!")
    st.info(f"Analysis saved to: {saved_folder}")

st.divider()

# ============================================================
# ATS Match Dashboard
# ============================================================

match = st.session_state.get("match_result")

if match:

    score = match.get("match_score", 0)
    score_breakdown = match.get("score_breakdown", {})

    required_score = score_breakdown.get("required_score", 0)
    preferred_score = score_breakdown.get("preferred_score", 0)

    matched = match.get("matched_skills", [])
    missing = match.get("missing_skills", [])

    required_matched = match.get("required_matched", [])
    required_missing = match.get("required_missing", [])

    preferred_matched = match.get("preferred_matched", [])
    preferred_missing = match.get("preferred_missing", [])

    status_text, status_class = get_score_status(score)

    st.markdown("## 🎯 ATS Match Dashboard")

    # --------------------------------------------------------
    # Score Cards
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        render_metric_card("Overall ATS Score", f"{score}%")

    with col2:
        render_metric_card("Required Skills Score", f"{required_score}%")

    with col3:
        render_metric_card("Preferred Skills Score", f"{preferred_score}%")

    st.progress(score / 100)

    # --------------------------------------------------------
    # Match Status Card
    # --------------------------------------------------------

    if score >= 85:
        advice = "Your resume aligns very strongly with this role."
    elif score >= 70:
        advice = "Your resume is a good match. Strengthening the missing skills will improve your chances."
    elif score >= 50:
        advice = "Your resume partially matches this role. Focus on the missing required skills before applying."
    else:
        advice = "Your resume needs significant tailoring before applying to this role."

    st.markdown(
    f"""
    <div class="status-card">
        <h3>Match Status</h3>
        <span class="status-pill {status_class}">{status_text}</span>
        <p>{advice}</p>
    </div>
    """,
    unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # Skill Counts
    # --------------------------------------------------------

    count_col1, count_col2 = st.columns(2)

    with count_col1:
        render_metric_card("Matched Skills", len(matched))

    with count_col2:
        render_metric_card("Missing Skills", len(missing))

    # --------------------------------------------------------
    # Matched / Missing Skills
    # --------------------------------------------------------

    st.markdown("### ✅ Matched Skills")
    render_skill_pills(matched)

    st.markdown("### ❌ Missing Skills")
    render_skill_pills(missing, missing=True)

    # --------------------------------------------------------
    # Required Skills
    # --------------------------------------------------------

    st.markdown("### Required Skills Breakdown")

    req_col1, req_col2 = st.columns(2)

    with req_col1:
        st.markdown("#### ✅ Required Matched")
        render_skill_pills(required_matched)

    with req_col2:
        st.markdown("#### ❌ Required Missing")
        render_skill_pills(required_missing, missing=True)

    # --------------------------------------------------------
    # Preferred Skills
    # --------------------------------------------------------

    st.markdown("### Preferred Skills Breakdown")

    pref_col1, pref_col2 = st.columns(2)

    with pref_col1:
        st.markdown("#### ✅ Preferred Matched")
        render_skill_pills(preferred_matched)

    with pref_col2:
        st.markdown("#### ❌ Preferred Missing")
        render_skill_pills(preferred_missing, missing=True)

    # --------------------------------------------------------
    # Category Performance
    # --------------------------------------------------------

    category_scores = score_breakdown.get("category_scores", {})

    if category_scores:

        st.markdown("### 📊 Category Performance")

        for category, data in category_scores.items():

            category_score = data.get("score", 0)

            with st.expander(f"{category} — {category_score}%"):

                c1, c2 = st.columns(2)

                with c1:
                    st.markdown("**Matched**")
                    render_skill_pills(data.get("matched", []))

                with c2:
                    st.markdown("**Missing**")
                    render_skill_pills(data.get("missing", []), missing=True)

else:

    st.info("Generate the application package to view ATS match results.")
        


# ============================================================
# AI Recommendations
# ============================================================

recommendations = st.session_state.get("recommendations")

st.markdown("## 🤖 AI Career Coach")


def coach_clean_text(value):
    if value is None:
        return ""

    text = str(value)
    text = html_lib.unescape(text)

    # Remove markdown/code fences and inline backticks
    text = text.replace("```html", "")
    text = text.replace("```", "")
    text = text.replace("`", "")

    # If it is only a broken HTML tag, remove it completely
    stripped = text.strip().lower()

    if stripped in [
        "<div>",
        "</div>",
        "<div></div>",
        "</div></div>",
        "&lt;div&gt;",
        "&lt;/div&gt;",
        "&lt;/div&gt;&lt;/div&gt;",
        "/div",
        "div"
    ]:
        return ""

    # Remove div tags but keep useful inner text
    text = re.sub(
        r"</?div[^>]*>",
        " ",
        text,
        flags=re.IGNORECASE
    )

    # Remove any other HTML tags
    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    broken_fragments = [
        "gap-item",
        "gap-title",
        "gap-text",
        "class=",
        "</div>",
        "<div>",
        "&lt;/div&gt;",
        "&lt;div&gt;"
    ]

    for fragment in broken_fragments:
        text = text.replace(fragment, " ")

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    if text.lower() in ["", "none", "n/a", "null", "/div", "div"]:
        return ""

    return html_lib.escape(text)


def coach_ensure_list(value):
    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]


def coach_is_html_garbage(value):
    if value is None:
        return True

    text = str(value).strip()
    text = html_lib.unescape(text).strip().lower()

    # Remove common markdown/code formatting
    text = text.replace("`", "").strip()

    garbage_values = [
        "",
        "<div>",
        "</div>",
        "<div></div>",
        "</div></div>",
        "&lt;div&gt;",
        "&lt;/div&gt;",
        "&lt;/div&gt;&lt;/div&gt;",
        "/div",
        "div"
    ]

    if text in garbage_values:
        return True

    if "<div" in text:
        return True

    if "</div" in text:
        return True

    if "class=" in text:
        return True

    if "gap-item" in text:
        return True

    if "gap-title" in text:
        return True

    if "gap-text" in text:
        return True

    return False


def coach_skill_pills(skills, missing=False):
    css_class = "missing-pill" if missing else "skill-pill"
    pills_html = ""

    for skill in coach_ensure_list(skills):
        if coach_is_html_garbage(skill):
            continue

        clean_skill = coach_clean_text(skill)

        if clean_skill:
            pills_html += f'<span class="{css_class}">{clean_skill}</span>'

    if not pills_html.strip():
        return "<p>No items available.</p>"

    return pills_html


def coach_build_gap_html(gaps):
    gap_html = ""

    for gap in coach_ensure_list(gaps):
        if coach_is_html_garbage(gap):
            continue

        if isinstance(gap, dict):
            skill_name = coach_clean_text(gap.get("skill_name", ""))
            recommendation = coach_clean_text(gap.get("recommendation", ""))
        else:
            skill_name = coach_clean_text(gap)
            recommendation = ""

        if not skill_name and not recommendation:
            continue

        if coach_is_html_garbage(skill_name) or coach_is_html_garbage(recommendation):
            continue

        gap_html += f"""
        <div class="gap-item">
            <div class="gap-title">{skill_name}</div>
            <div class="gap-text">{recommendation}</div>
        </div>
        """

    if not gap_html.strip():
        return "<p>No major priority gaps found.</p>"

    return gap_html


def coach_build_improvements_html(improvements):
    improvements_html = ""

    for item in coach_ensure_list(improvements):
        if coach_is_html_garbage(item):
            continue

        if isinstance(item, dict):
            point = coach_clean_text(item.get("improvement_point", ""))
            recommendation = coach_clean_text(item.get("recommendation", ""))
        else:
            point = ""
            recommendation = coach_clean_text(item)

        if not point and not recommendation:
            continue

        improvements_html += f"""
        <div class="gap-item">
            <div class="gap-title">{point}</div>
            <div class="gap-text">{recommendation}</div>
        </div>
        """

    if not improvements_html.strip():
        return "<p>No improvements suggested.</p>"

    return improvements_html


def coach_build_learning_html(items):
    learning_html = ""

    for item in coach_ensure_list(items):
        if coach_is_html_garbage(item):
            continue

        item_text = coach_clean_text(item)

        if not item_text:
            continue

        if coach_is_html_garbage(item_text):
            continue

        learning_html += f"""
        <div class="gap-item">
            <div class="gap-text">{item_text}</div>
        </div>
        """

    if not learning_html.strip():
        return "<p>No learning recommendations available.</p>"

    return learning_html


if recommendations and isinstance(recommendations, dict) and "error" not in recommendations:

    summary = coach_clean_text(
        recommendations.get(
            "executive_summary",
            "No summary generated."
        )
    )

    strengths = [
        item
        for item in coach_ensure_list(recommendations.get("top_strengths", []))
        if not coach_is_html_garbage(item)
    ]

    gaps = [
        item
        for item in coach_ensure_list(recommendations.get("critical_skill_gaps", []))
        if not coach_is_html_garbage(item)
    ]

    improvements = [
        item
        for item in coach_ensure_list(recommendations.get("resume_improvements", []))
        if not coach_is_html_garbage(item)
    ]

    ats_keywords = [
        item
        for item in coach_ensure_list(recommendations.get("ats_keywords", []))
        if not coach_is_html_garbage(item)
    ]

    learning = [
        item
        for item in coach_ensure_list(recommendations.get("learning_recommendations", []))
        if not coach_is_html_garbage(item)
    ]

    st.markdown(
        f"""
        <div class="coach-card">
            <h3>📋 Executive Summary</h3>
            <p>{summary}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            <div class="coach-card">
                <h3>💪 Strengths</h3>
                {coach_skill_pills(strengths)}
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
               f"""
        <div class="coach-card">
              <h3>🚀 Priority Gaps</h3>
              {coach_build_gap_html(gaps)}
        </div>
                          """,
            unsafe_allow_html=True
        )

    st.markdown(
        f"""
        <div class="coach-card">
            <h3>📝 Resume Improvements</h3>
            {coach_build_improvements_html(improvements)}
        </div>
        """,
        unsafe_allow_html=True
    )

    col3, col4 = st.columns(2)

    with col3:
        st.markdown(
            f"""
            <div class="coach-card">
                <h3>🎯 ATS Keywords</h3>
                {coach_skill_pills(ats_keywords)}
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"""
            <div class="coach-card">
                <h3>📚 Learning Recommendations</h3>
                {coach_build_learning_html(learning)}
        </div>
            """,
            unsafe_allow_html=True
        )

else:
    st.markdown(
        """
        <div class="warning-box">
            Career coach recommendations are not available yet.
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# Downloads / Application Package
# ============================================================

st.divider()

st.markdown("## 📦 Application Package")

tailored_resume = st.session_state.get("tailored_resume")
cover_letter = st.session_state.get("cover_letter")

resume_ready = tailored_resume and "error" not in tailored_resume
cover_ready = cover_letter and "error" not in cover_letter

if resume_ready or cover_ready:

    st.markdown(
        """
        <div class="success-box">
            ✅ Your application package is ready. Download your generated documents below.
        </div>
        """,
        unsafe_allow_html=True
    )

    download_col1, download_col2 = st.columns(2)

    # --------------------------------------------------------
    # Tailored Resume Download
    # --------------------------------------------------------

    with download_col1:

        st.markdown(
            """
            <div class="section-card">
                <h3>📄 Tailored Resume</h3>
                <p style="color:#6b7280;">
                    Optimized resume version aligned with the selected job description.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if resume_ready:

            exporter = DocxExporter(tailored_resume)
            output_file = exporter.export()

            with open(output_file, "rb") as file:

                st.download_button(
                    "Download Tailored Resume",
                    data=file,
                    file_name=output_file.name,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                    key="download_resume"
                )

        else:

            st.info("Tailored resume is not available yet.")

    # --------------------------------------------------------
    # Cover Letter Download
    # --------------------------------------------------------

    with download_col2:

        st.markdown(
            """
            <div class="section-card">
                <h3>✉️ Cover Letter</h3>
                <p style="color:#cbd5e1">
                    Personalized cover letter generated from your resume and target role.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if cover_ready:

            exporter = CoverLetterExporter(
                cover_letter,
                st.session_state["resume_json"]
            )

            output_file = exporter.export()

            with open(output_file, "rb") as file:

                st.download_button(
                    "Download Cover Letter",
                    data=file,
                    file_name=output_file.name,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                    key="download_cover_letter"
                )

        else:

            st.info("Cover letter is not available yet.")

else:

    st.markdown(
        """
        <div class="warning-box">
            Generate the application package to unlock resume and cover letter downloads.
        </div>
        """,
        unsafe_allow_html=True
    )
        

with st.expander("🛠 Developer Tools", expanded=False):

    if st.session_state.get("resume_text"):
        st.markdown("### Extracted Resume Text")
        st.text_area(
            "Resume Text",
            st.session_state["resume_text"],
            height=250
        )

    if st.session_state.get("resume_json"):
        st.markdown("### Resume JSON")
        st.json(st.session_state["resume_json"])

    if st.session_state.get("jd_json"):
        st.markdown("### Job Description JSON")
        st.json(st.session_state["jd_json"])

    if st.session_state.get("match_result"):
        st.markdown("### Match Result JSON")
        st.json(st.session_state["match_result"])

    if st.session_state.get("recommendations"):
        st.markdown("### Recommendation JSON")
        st.json(st.session_state["recommendations"])

    if st.session_state.get("tailored_resume"):
        st.markdown("### Tailored Resume JSON")
        st.json(st.session_state["tailored_resume"])