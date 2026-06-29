from pathlib import Path
import re

from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

class CoverLetterExporter:

    def __init__(self, cover_letter_json, resume_json):

        self.cover_letter = cover_letter_json
        
        self.resume = resume_json

        self.document = Document()

        self.output_folder = Path("outputs")

        self.output_folder.mkdir(exist_ok=True)
        
    def setup_document(self):

        section = self.document.sections[0]

        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

        style = self.document.styles["Normal"]

        style.font.name = "Calibri"

        style.font.size = Pt(11)
        
    def add_letter(self):

        letter = self.cover_letter.get("cover_letter", "")

        paragraphs = letter.split("\n")

        for paragraph in paragraphs:

            paragraph = paragraph.strip()

            if paragraph:

                self.document.add_paragraph(paragraph)
                
    def save_document(self):

        personal = self.resume.get("personal_information", {})

        name = personal.get("name", "Cover_Letter").strip()

        safe_name = re.sub(r'[\\/*?:"<>|]', "", name)

        safe_name = safe_name.replace(" ", "_")

        filename = f"{safe_name}_Cover_Letter.docx"

        output_file = self.output_folder / filename

        self.document.save(output_file)

        return output_file
    
    def export(self):
        self.setup_document()

        self.add_letter()

        return self.save_document()
    