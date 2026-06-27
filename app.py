import streamlit as st

from modules.parser import ResumeParser
from modules.resume_analyzer import ResumeAnalyzer
from modules.jd_analyzer import JDAnalyzer
from modules.matcher import ResumeMatcher
from modules.recommendation_engine import RecommendationEngine
from modules.resume_generator import ResumeGenerator
from modules.exporter import Exporter
from modules.docx_exporter import DocxExporter

# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="ResumePilot AI",
    page_icon="📄",
    layout="wide"
)


# ============================================================
# Session State
# ============================================================

DEFAULT_STATE = {
    "resume_json": None,
    "jd_json": None,
    "match_result": None,
    "recommendations": None,
    "tailored_resume": None
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# Header
# ============================================================

st.title("📄 ResumePilot AI")
st.caption("AI Powered Resume Tailoring Assistant")

st.divider()


# ============================================================
# Resume Upload
# ============================================================

st.header("📄 Upload Resume")

uploaded_file = st.file_uploader(
    "Upload your Resume (PDF or DOCX)",
    type=["pdf", "docx"]
)

resume_text = None

if uploaded_file is not None:

    try:

        resume_text = ResumeParser.extract_text(uploaded_file)

        analyzer = ResumeAnalyzer()

        with st.spinner("Analyzing resume..."):
            st.session_state["resume_json"] = analyzer.analyze(resume_text)

        st.success("Resume analyzed successfully.")

        # ------------------------------------------
        # Extracted Resume
        # ------------------------------------------

        with st.expander("📄 Extracted Resume Text"):

            st.text_area(
                "Resume",
                value=resume_text,
                height=350
            )

        # ------------------------------------------
        # Structured Resume
        # ------------------------------------------

        with st.expander("🤖 Structured Resume JSON"):

            st.json(
                st.session_state["resume_json"]
            )

    except Exception as e:

        st.error(e)


st.divider()


# ============================================================
# Job Description
# ============================================================

st.header("📝 Job Description")

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

            st.success("Job Description analyzed successfully.")

            with st.expander("🤖 Structured Job Description JSON"):

                st.json(
                    st.session_state["jd_json"]
                )

        except Exception as e:

            st.error(f"AI Analysis Failed\n\n{e}")


st.divider()


# ============================================================
# Resume Matching
# ============================================================

st.header("🎯 Resume Matching")

compare_button = st.button(
    "Compare Resume with Job Description",
    use_container_width=True
)

if compare_button:

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    if st.session_state["resume_json"] is None:
        st.warning("Please upload a resume first.")
        st.stop()

    if st.session_state["jd_json"] is None:
        st.warning("Please analyze a Job Description first.")
        st.stop()

    # --------------------------------------------------------
    # Skill Matching
    # --------------------------------------------------------

    with st.spinner("Matching resume against job description..."):

        matcher = ResumeMatcher(
            st.session_state["resume_json"],
            st.session_state["jd_json"]
        )

        match_result = matcher.match()

        st.session_state["match_result"] = match_result

    # --------------------------------------------------------
    # AI Recommendations
    # --------------------------------------------------------

    with st.spinner("Generating AI recommendations..."):

        recommendation_engine = RecommendationEngine()

        recommendations = recommendation_engine.generate(
            st.session_state["resume_json"],
            st.session_state["jd_json"],
            match_result
        )

        st.session_state["recommendations"] = recommendations

    # --------------------------------------------------------
    # Tailored Resume
    # --------------------------------------------------------

    with st.spinner("Generating tailored resume..."):

        generator = ResumeGenerator()

        tailored_resume = generator.generate(
            st.session_state["resume_json"],
            st.session_state["jd_json"],
            match_result,
            recommendations
        )

        st.session_state["tailored_resume"] = tailored_resume

    # --------------------------------------------------------
    # Save Analysis
    # --------------------------------------------------------

    saved_folder = Exporter.save_analysis(
        st.session_state["resume_json"],
        st.session_state["jd_json"],
        match_result
    )

    st.success("Analysis completed successfully!")

    st.info(f"Analysis saved to: {saved_folder}")

st.divider()

# ============================================================
# Results Dashboard
# ============================================================

st.header("📊 Analysis Dashboard")

# ------------------------------------------------------------
# Match Results
# ------------------------------------------------------------

if st.session_state["match_result"]:

    result = st.session_state["match_result"]

    st.subheader("🎯 ATS Match Score")

    st.metric(
        "Resume Match",
        f"{result['match_score']}%"
    )

    st.progress(result["match_score"] / 100)

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("✅ Matched Skills")

        if result["matched_skills"]:

            for skill in result["matched_skills"]:
                st.success(skill)

        else:

            st.info("No matched skills found.")

    with col2:

        st.subheader("❌ Missing Skills")

        if result["missing_skills"]:

            for skill in result["missing_skills"]:
                st.error(skill)

        else:

            st.success("No missing skills!")

st.divider()


# ============================================================
# AI Recommendations
# ============================================================

recommendations = st.session_state.get("recommendations")

if recommendations:

    st.header("🤖 AI Recommendations")

    if "error" in recommendations:

        st.error(recommendations["error"])

        with st.expander("Raw AI Response"):

            st.code(recommendations["raw_response"])

    else:

        # Executive Summary

        st.subheader("📋 Executive Summary")
        st.info(
            recommendations.get(
                "executive_summary",
                "No summary generated."
            )
        )

        # Strengths

        st.subheader("💪 Top Strengths")

        strengths = recommendations.get(
            "top_strengths",
            []
        )

        if strengths:

            for item in strengths:

                if isinstance(item, dict):

                    st.success(
                        item.get(
                            "strength",
                            str(item)
                        )
                    )

                else:

                    st.success(item)

        else:

            st.write("No strengths returned.")

        # Skill Gaps

        st.subheader("⚠️ Critical Skill Gaps")

        gaps = recommendations.get(
            "critical_skill_gaps",
            []
        )

        if gaps:

            for gap in gaps:

                if isinstance(gap, dict):

                    st.error(
                        f"**{gap.get('skill_name','')}**\n\n"
                        f"{gap.get('recommendation','')}"
                    )

                else:

                    st.error(str(gap))

        else:

            st.write("No skill gaps returned.")

        # Resume Improvements

        st.subheader("📝 Resume Improvements")

        improvements = recommendations.get(
            "resume_improvements",
            []
        )

        if improvements:

            for improvement in improvements:

                if isinstance(improvement, dict):

                    st.warning(
                        f"**{improvement.get('improvement_point','')}**\n\n"
                        f"{improvement.get('recommendation','')}"
                    )

                else:

                    st.warning(str(improvement))

        else:

            st.write("No improvements suggested.")

        # ATS Keywords

        st.subheader("🎯 ATS Keywords")

        keywords = recommendations.get("ats_keywords", [])

        if keywords:

            formatted_keywords = []

            for keyword in keywords:

                if isinstance(keyword, str):
                    formatted_keywords.append(keyword)

                elif isinstance(keyword, dict):
                    # If the AI returns {"keyword": "..."} or any similar dict,
                    # collect all string values.
                    for value in keyword.values():
                        if isinstance(value, str):
                            formatted_keywords.append(value)

                else:
                    formatted_keywords.append(str(keyword))

            st.write(", ".join(formatted_keywords))

        else:

            st.write("No ATS keywords generated.")

        # Learning

        st.subheader("📚 Learning Recommendations")

        learning = recommendations.get(
            "learning_recommendations",
            []
        )

        if learning:

            for item in learning:

                st.info(item)

        else:

            st.write("No learning recommendations.")

st.divider()


# ============================================================
# Tailored Resume
# ============================================================

tailored = st.session_state.get("tailored_resume")

if tailored:

    st.header("✨ Tailored Resume")

    if "error" in tailored:

        st.error(tailored["error"])

        with st.expander("Raw AI Response"):

            st.code(tailored["raw_response"])

    else:

        st.success("Tailored resume generated successfully!")

        st.json(tailored)
        
st.divider()

st.header("📄 Export Resume")

tailored_resume = st.session_state.get("tailored_resume")

if tailored_resume and "error" not in tailored_resume:

    exporter = DocxExporter(tailored_resume)

    output_file = exporter.export()

    with open(output_file, "rb") as file:

        st.download_button(
            label="📥 Download Tailored Resume (.docx)",
            data=file,
            file_name=output_file.name,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )