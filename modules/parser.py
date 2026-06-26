from docx import Document
import pdfplumber
import os


class ResumeParser:
    """
    Handles extracting text from PDF and DOCX resume files.
    """

    @staticmethod
    def extract_text(file):
        """
        Extract text from an uploaded Streamlit file.

        Parameters:
            file: Uploaded file from Streamlit

        Returns:
            str: Extracted resume text
        """

        file_extension = os.path.splitext(file.name)[1].lower()

        if file_extension == ".pdf":
            return ResumeParser._extract_pdf(file)

        elif file_extension == ".docx":
            return ResumeParser._extract_docx(file)

        else:
            raise ValueError("Unsupported file format. Please upload a PDF or DOCX file.")

    @staticmethod
    def _extract_pdf(file):
        text = ""

        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        return text

    @staticmethod
    def _extract_docx(file):
        document = Document(file)

        paragraphs = []

        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                paragraphs.append(paragraph.text)

        return "\n".join(paragraphs)