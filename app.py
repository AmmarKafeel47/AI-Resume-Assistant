import streamlit as st
from modules.parser import ResumeParser

st.set_page_config(
    page_title="ResumePilot AI",
    page_icon="📄",
    layout="wide"
)

st.title("📄 ResumePilot AI")
st.subheader("Sprint 2 - Resume Parser")

uploaded_file = st.file_uploader(
    "Upload your Resume (PDF or DOCX)",
    type=["pdf", "docx"]
)

if uploaded_file:

    try:
        resume_text = ResumeParser.extract_text(uploaded_file)

        st.success("Resume uploaded successfully!")

        st.subheader("Extracted Resume Text")

        st.text_area(
            label="Resume Content",
            value=resume_text,
            height=500
        )

    except Exception as e:
        st.error(f"Error: {e}")