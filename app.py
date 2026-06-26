import streamlit as st
from modules.parser import ResumeParser
from modules.jd_analyzer import JDAnalyzer

st.set_page_config(
    page_title="ResumePilot AI",
    page_icon="📄",
    layout="wide"
)

st.title("📄 ResumePilot AI")
st.markdown("### AI Powered Resume Tailoring Assistant")

st.divider()

# -------------------------
# Resume Upload
# -------------------------

st.header("📄 Resume")

uploaded_file = st.file_uploader(
    "Upload your Resume (PDF or DOCX)",
    type=["pdf", "docx"]
)

resume_text = None

if uploaded_file:

    try:
        resume_text = ResumeParser.extract_text(uploaded_file)

        st.success("Resume uploaded successfully!")

        with st.expander("View Extracted Resume"):
            st.text_area(
                "Resume Content",
                value=resume_text,
                height=400
            )

    except Exception as e:
        st.error(e)

st.divider()

# -------------------------
# Job Description
# -------------------------

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

st.divider()

# -------------------------
# Results
# -------------------------

st.header("📊 Analysis Results")

if analyze_button:

    if not job_description.strip():

        st.warning("Please paste a job description.")

    else:

        try:
            analyzer = JDAnalyzer()

            with st.spinner("Analyzing Job Description..."):
                analysis = analyzer.analyze(job_description)

            st.success("Analysis Complete!")

            st.json(analysis)
        except Exception as e:
            st.error(f"AI Analysis Failed:\n\n{e}")
       