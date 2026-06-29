import streamlit as st

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
st.divider()

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

    with st.expander("🛠 Developer Tools"):

        st.subheader("📄 Extracted Resume Text")

        st.text_area(
            "Resume",
            value=resume_text,
            height=350
        )

        st.subheader("🤖 Structured Resume JSON")

        st.json(resume)
#with st.expander("🛠 Developer Tools"):

  #  st.subheader("📄 Extracted Resume Text")

   # st.text_area(
    #    "Resume",
     #   value=resume_text,
      #  height=350
    #)

    #st.subheader("🤖 Structured Resume JSON")

    #st.json(st.session_state["resume_json"])

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

    with st.expander("🛠 Developer Tools"):

        st.subheader("🤖 Job Description JSON")

        st.json(jd)
                

        


st.divider()


# ============================================================
# Resume Matching
# ============================================================

st.header("🎯 Resume Matching")

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

        st.session_state["tailored_resume"] = generator.generate(
            st.session_state["resume_json"],
            st.session_state["jd_json"],
            st.session_state["match_result"],
            st.session_state["recommendations"]
        )

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
# ATS Match Results
# ============================================================

match = st.session_state.get("match_result")

if match:

    score = match.get("match_score", 0)

    if score >= 85:
        rating = "🟢 Excellent Match"
        advice = "Your resume aligns very well with this role. Address the remaining missing skills to maximize ATS performance."

    elif score >= 70:
        rating = "🟡 Good Match"
        advice = "Your resume is a good match. Strengthening the missing skills will improve your chances."

    elif score >= 50:
        rating = "🟠 Fair Match"
        advice = "Your resume partially matches this role. Consider tailoring your experience and skills."

    else:
        rating = "🔴 Needs Improvement"
        advice = "Your resume needs significant tailoring before applying."

    matched = match.get("matched_skills", [])
    missing = match.get("missing_skills", [])

    st.subheader("🎯 ATS Match Results")

    st.metric(
        "Overall Match Score",
        f"{score}%"
    )

    st.progress(score / 100)

    st.success(rating)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "✅ Matched Skills",
            len(matched)
        )

    with col2:

        st.metric(
            "❌ Missing Skills",
            len(missing)
        )

    st.divider()

    st.info(advice)

    st.divider()

    st.subheader("✅ Matched Skills")

    if matched:

        st.write(" • ".join(matched))

    else:

        st.info("No matched skills found.")

    st.subheader("❌ Missing Skills")

    if missing:

        st.write(" • ".join(missing))

    else:

        st.success("No missing skills!")

    st.divider()

    with st.expander("🛠 Developer Tools"):

        st.subheader("Match Result JSON")

        st.json(match)
        
        
        
# ============================================================
# AI Recommendations
# ============================================================

recommendations = st.session_state.get("recommendations")

if recommendations:

    st.header("🤖 AI Career Coach")

    if "error" in recommendations:

        st.error(recommendations["error"])

        with st.expander("🛠 Developer Tools"):

            st.subheader("Recommendation JSON")

            st.json(recommendations)

            if "raw_response" in recommendations:

                st.subheader("Raw AI Response")

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

        st.subheader("💪 Your Strengths")

        strengths = recommendations.get("top_strengths", [])

        if strengths:

            formatted = []

            for item in strengths:

                if isinstance(item, dict):
                    formatted.append(item.get("strength", ""))

                else:
                    formatted.append(str(item))

            st.write(" • ".join(formatted))

        else:

            st.info("No strengths identified.")

        # Skill Gaps

        st.subheader("🚀 Priority Improvements")

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

            st.write("• ".join(formatted_keywords))

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
# --------------------------------------------------------
# Developer Tools
# --------------------------------------------------------

with st.expander("🛠 Developer Tools"):

    st.subheader("🤖 Recommendation JSON")

    st.json(recommendations)
    
    tailored_resume = st.session_state.get("tailored_resume")

    if tailored_resume:

        st.subheader("📄 Tailored Resume JSON")
        st.json(tailored_resume)

    if "raw_response" in recommendations:

        st.subheader("📝 Raw AI Response")

        st.code(recommendations["raw_response"])

st.divider()


# ============================================================
# Tailored Resume
# ============================================================
        
#st.divider()

#st.header("📄 Export Resume")
# ============================================================
# Downloads
# ============================================================

st.divider()

st.header("📦 Downloads")

tailored_resume = st.session_state.get("tailored_resume")

if tailored_resume and "error" not in tailored_resume:

    exporter = DocxExporter(tailored_resume)

    output_file = exporter.export()

    with open(output_file, "rb") as file:

        st.download_button(
            "📄 Download Tailored Resume",
            data=file,
            file_name=output_file.name,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            key="download_resume"
        )

cover_letter = st.session_state.get("cover_letter")

if cover_letter and "error" not in cover_letter:

    exporter = CoverLetterExporter(
        cover_letter,
        st.session_state["resume_json"]
    )

    output_file = exporter.export()

    with open(output_file, "rb") as file:

        st.download_button(
            "✉️ Download Cover Letter",
            data=file,
            file_name=output_file.name,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            key="download_cover_letter"
        )
#tailored_resume = st.session_state.get("tailored_resume")

#if tailored_resume and "error" not in tailored_resume:

 #   exporter = DocxExporter(tailored_resume)

  #  output_file = exporter.export()

   # with open(output_file, "rb") as file:

    #    st.download_button(
      #      label="📥 Download Tailored Resume (.docx)",
     #       data=file,
       #     file_name=output_file.name,
        #    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
         #   use_container_width=True
        #)         
        
#st.divider()

#st.header("✉️ Export Cover Letter")

#cover_letter = st.session_state.get("cover_letter")

#if cover_letter and "error" not in cover_letter:

 #   exporter = CoverLetterExporter(
  #      cover_letter,
   #     st.session_state["resume_json"]
    #)

    #output_file = exporter.export()

    #with open(output_file, "rb") as file:

     #   st.download_button(
      #      label="📥 Download Cover Letter (.docx)",
       #     data=file,
        #    file_name=output_file.name,
         #   mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
          #  use_container_width=True
        #)