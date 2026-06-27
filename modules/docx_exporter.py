from pathlib import Path
from pdb import run

from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

import re

class DocxExporter:

    def __init__(self, resume_json):

        self.resume = resume_json
        self.document = Document()

        self.output_folder = Path("outputs")
        self.output_folder.mkdir(exist_ok=True)
        
    def set_default_font(self):

        styles = self.document.styles

        normal_style = styles["Normal"]

        normal_style.font.name = "Calibri"

        normal_style.font.size = Pt(11)
        
    def add_section_heading(self, title):

        paragraph = self.document.add_paragraph()

        paragraph.space_before = Pt(12)
        paragraph.space_after = Pt(6)

        run = paragraph.add_run(title.upper())

        run.bold = True
        run.font.size = Pt(14)

    def add_header(self):

        personal = self.resume.get("personal_information", {})

        name = personal.get("name", "").strip()
        email = personal.get("email", "").strip()
        phone = personal.get("phone", "").strip()
        linkedin = personal.get("linkedin", "").strip()
        github = personal.get("github", "").strip()

        headline = self.resume.get("headline", "").strip()

        # -------------------------
        # Name
        # -------------------------

        heading = self.document.add_heading(name, level=0)
        heading.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        # -------------------------
        # Headline
        # -------------------------

        if headline:

            paragraph = self.document.add_paragraph()
            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

            run = paragraph.add_run(headline)
            run.bold = True
            run.font.size = Pt(13)

        # -------------------------
        # Email | Phone
        # -------------------------

        contact = []

        if email:
            contact.append(email)

        if phone:
            contact.append(phone)

        if contact:

            paragraph = self.document.add_paragraph(
                " | ".join(contact)
            )

            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        # -------------------------
        # LinkedIn | GitHub
        # -------------------------

        social = []

        if linkedin:
            social.append(linkedin)

        if github:
            social.append(github)

        if social:

            paragraph = self.document.add_paragraph(
                " | ".join(social)
            )

            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        self.document.add_paragraph()
        
    def add_summary(self):

        summary = self.resume.get("summary", "").strip()

        if not summary:
            return

        self.add_section_heading("Professional Summary")

        paragraph = self.document.add_paragraph()

        paragraph.add_run(summary)
        
    def add_skills(self):

        skills = self.resume.get("skills", {})

        if not skills:
            return

        self.add_section_heading("Technical Skills")

        for category, items in skills.items():

            if not items:
                continue

            category_name = category.replace("_", " ").title()

            paragraph = self.document.add_paragraph()

            run = paragraph.add_run(category_name)

            run.bold = True

            for item in items:

                bullet = self.document.add_paragraph(
                    item,
                    style="List Bullet"
                )

        self.document.add_paragraph()    
        
    def add_experience(self):

        experience = self.resume.get("experience", [])

        if not experience:
            return

        self.add_section_heading("Professional Experience")

        for job in experience:

            # Job Title
            title = self.document.add_paragraph()

            run = title.add_run(
                job.get("job_title", "")
            )

            run.bold = True
            run.font.size = Pt(12)

            # Company | Location
            company_line = self.document.add_paragraph()

            company = job.get("company", "")
            location = job.get("location", "")

            company_line.add_run(
                f"{company} | {location}"
            )

            # Dates
            dates = self.document.add_paragraph()

            dates.add_run(
                f"{job.get('start_date','')} - {job.get('end_date','')}"
            )

            # Responsibilities
            for responsibility in job.get("responsibilities", []):

                self.document.add_paragraph(
                    responsibility,
                    style="List Bullet"
                )

            self.document.add_paragraph()    
            
    def add_projects(self):

        projects = self.resume.get("projects", [])

        if not projects:
            return

        self.add_section_heading("Projects")

        for project in projects:

            # Project Title
            title = self.document.add_paragraph()

            run = title.add_run(
                project.get("title", "")
            )

            run.bold = True
            run.font.size = Pt(12)

            # Description
            description = project.get("description", "").strip()

            if description:
                self.document.add_paragraph(description)

            # Technologies
            technologies = project.get("technologies", [])

            if technologies:

                tech_heading = self.document.add_paragraph()

                tech_run = tech_heading.add_run("Technologies: ")

                tech_run.bold = True

                tech_heading.add_run(", ".join(technologies))

            self.document.add_paragraph()
            
    def add_education(self):

        education = self.resume.get("education", [])

        if not education:
            return

        self.add_section_heading("Education")

        for edu in education:

            # Degree
            degree = self.document.add_paragraph()

            run = degree.add_run(
                edu.get("degree", "")
            )

            run.bold = True
            run.font.size = Pt(12)

            # Institution
            institution = edu.get("institution", "")

            if institution:
                self.document.add_paragraph(institution)

            # Dates
            dates = edu.get("dates", "")

            if dates:
                self.document.add_paragraph(dates)

            # Description
            description = edu.get("description", "")

            if description:
                self.document.add_paragraph(description)

            self.document.add_paragraph()
    

    def add_certifications(self):

        certifications = self.resume.get("certifications", [])

        if not certifications:
            return

        self.add_section_heading("Certifications")

        for certification in certifications:

            self.document.add_paragraph(
                certification,
                style="List Bullet"
            )

        self.document.add_paragraph()
        
    def add_languages(self):

        languages = self.resume.get("languages", [])

        if not languages:
            return

        self.add_section_heading("Languages")

        for language in languages:

            name = language.get("language", "").strip()
            proficiency = language.get("proficiency", "").strip()

            if name and proficiency:
                text = f"{name} — {proficiency}"
            else:
                text = name or proficiency

            self.document.add_paragraph(
                text,
                style="List Bullet"
            )

        self.document.add_paragraph()

    def setup_document(self):

        section = self.document.sections[0]

        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)

        self.set_default_font()

    def save_document(self):

        personal = self.resume.get("personal_information", {})

        name = personal.get("name", "Resume").strip()

        # Replace invalid filename characters
        safe_name = re.sub(r'[\\/*?:"<>|]', "", name)

        # Replace spaces with underscores
        safe_name = safe_name.replace(" ", "_")

        filename = f"{safe_name}_Tailored_Resume.docx"

        output_file = self.output_folder / filename

        self.document.save(output_file)

        return output_file
    
    def export(self):

        self.setup_document()

        self.add_header()

        self.add_summary()
        
        self.add_skills()
        
        self.add_experience()

        self.add_projects()
        
        self.add_education()
        
        self.add_certifications()
        
        self.add_languages()
        
        return self.save_document()
    