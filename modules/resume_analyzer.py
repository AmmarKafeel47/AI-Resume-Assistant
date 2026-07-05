import json
import re

from services.ai.provider_factory import ProviderFactory
from modules.prompt_loader import PromptLoader


class ResumeAnalyzer:

    def __init__(self):
        self.ai = ProviderFactory.get_provider()

    def analyze(self, resume_text):

        prompt = PromptLoader.load(
            "prompts/analyze_resume.txt",
            {
                "RESUME": resume_text
            }
        )

        response = self.ai.generate(prompt)

        try:
            resume_json = json.loads(response)

        except json.JSONDecodeError:

            return {
                "error": "AI returned invalid JSON.",
                "raw_response": response
            }

        # Clean common Qwen extraction mistakes
        resume_json = self.clean_resume_json(resume_json, resume_text)

        return resume_json

    def clean_resume_json(self, resume_json, resume_text):
        """
        Fix predictable extraction issues without asking the AI again.
        """

        if not isinstance(resume_json, dict):
            return resume_json

        self.ensure_schema_keys(resume_json)
        self.fix_name_and_headline(resume_json, resume_text)
        self.clean_profile_links(resume_json)
        self.clean_education(resume_json)
        self.recover_missing_responsibilities(resume_json, resume_text)
        self.add_detected_skills(resume_json, resume_text)
        self.remove_unsupported_skills(resume_json, resume_text)

        return resume_json

    def ensure_schema_keys(self, resume_json):
        """
        Make sure required keys always exist.
        """

        resume_json.setdefault("personal_information", {})
        resume_json.setdefault("headline", "")
        resume_json.setdefault("summary", "")
        resume_json.setdefault("skills", {})
        resume_json.setdefault("experience", [])
        resume_json.setdefault("projects", [])
        resume_json.setdefault("education", [])
        resume_json.setdefault("certifications", [])
        resume_json.setdefault("languages", [])

        personal = resume_json["personal_information"]

        personal.setdefault("name", "")
        personal.setdefault("email", "")
        personal.setdefault("phone", "")
        personal.setdefault("linkedin", "")
        personal.setdefault("github", "")

        skills = resume_json["skills"]

        skills.setdefault("programming_languages", [])
        skills.setdefault("frameworks", [])
        skills.setdefault("databases", [])
        skills.setdefault("cloud", [])
        skills.setdefault("tools", [])
        skills.setdefault("soft_skills", [])

    def fix_name_and_headline(self, resume_json, resume_text):
        """
        Fix missing candidate name or headline using the top lines of the resume.
        """

        lines = [
            line.strip()
            for line in resume_text.splitlines()
            if line.strip()
        ]

        personal = resume_json.get("personal_information", {})

        # Fix missing name
        if not personal.get("name"):

            for index, line in enumerate(lines):

                if line.lower() == "resume" and index + 1 < len(lines):
                    personal["name"] = lines[index + 1]
                    break

        # Fix missing headline
        if not resume_json.get("headline"):

            name = personal.get("name", "").strip().lower()

            for index, line in enumerate(lines):

                if name and line.lower() == name and index + 1 < len(lines):

                    possible_headline = lines[index + 1].strip()

                    if (
                        possible_headline
                        and "@" not in possible_headline
                        and not possible_headline.lower().startswith("profile")
                    ):
                        resume_json["headline"] = possible_headline
                        break

    def clean_profile_links(self, resume_json):
        """
        Keep LinkedIn/GitHub only if real links are extracted.
        """

        personal = resume_json.get("personal_information", {})

        linkedin = str(personal.get("linkedin", "")).strip()
        github = str(personal.get("github", "")).strip()

        if "linkedin.com" not in linkedin.lower():
            personal["linkedin"] = ""

        if "github.com" not in github.lower():
            personal["github"] = ""

    def clean_education(self, resume_json):
        """
        Clean education fields:
        - Move Distinction / CGPA / grades from institution to description
        - Remove language text accidentally placed in education description
        """

        for edu in resume_json.get("education", []):

            institution = str(edu.get("institution", "")).strip()
            description = str(edu.get("description", "")).strip()

            # Remove language text from education description
            if "english" in description.lower() or "urdu" in description.lower():
                description = ""

            # Move Distinction from institution to description
            if "distinction" in institution.lower():

                institution = re.sub(
                    r"\s*\(?distinction\)?",
                    "",
                    institution,
                    flags=re.IGNORECASE
                ).strip()

                if "distinction" not in description.lower():
                    description = "Distinction"

            # Move CGPA from institution to description if it appears there
            cgpa_match = re.search(
                r"CGPA[:\s]*[0-9.]+",
                institution,
                flags=re.IGNORECASE
            )

            if cgpa_match:

                cgpa_text = cgpa_match.group(0)

                institution = institution.replace(cgpa_text, "").strip(" -|,()")

                if cgpa_text.lower() not in description.lower():
                    description = cgpa_text

            edu["institution"] = institution
            edu["description"] = description

    def recover_missing_responsibilities(self, resume_json, resume_text):
        """
        If AI leaves responsibilities empty, recover them from raw resume text.
        """

        experiences = resume_json.get("experience", [])

        if not experiences:
            return

        lines = [
            line.strip()
            for line in resume_text.splitlines()
            if line.strip()
        ]

        title_positions = {}

        for exp_index, exp in enumerate(experiences):

            job_title = str(exp.get("job_title", "")).strip().lower()

            if not job_title:
                continue

            for line_index, line in enumerate(lines):

                if job_title in line.lower():
                    title_positions[exp_index] = line_index
                    break

        project_start = len(lines)

        for index, line in enumerate(lines):

            if line.upper().startswith("PROJECTS"):
                project_start = index
                break

        for exp_index, exp in enumerate(experiences):

            if exp.get("responsibilities"):
                continue

            start_index = title_positions.get(exp_index)

            if start_index is None:
                continue

            possible_end_indexes = [
                position
                for index, position in title_positions.items()
                if position > start_index
            ]

            possible_end_indexes.append(project_start)

            end_index = min(possible_end_indexes)

            block_lines = lines[start_index + 1:end_index]

            responsibility_lines = []

            for line in block_lines:

                if line.upper().startswith("PROJECTS"):
                    break

                if "|" in line and re.search(r"\b20\d{2}\b", line):
                    break

                if len(line) >= 25:
                    responsibility_lines.append(line)

            recovered = self.convert_lines_to_bullets(responsibility_lines)

            if recovered:
                exp["responsibilities"] = recovered[:5]

    def convert_lines_to_bullets(self, lines):
        """
        Combine wrapped PDF lines into clean responsibility bullets.
        """

        bullets = []
        current = ""

        for line in lines:

            current = f"{current} {line}".strip()

            if re.search(r"[.!?%]$", line):
                bullets.append(current)
                current = ""

        if current:
            bullets.append(current)

        clean_bullets = []

        for bullet in bullets:

            bullet = re.sub(r"\s+", " ", bullet).strip()

            if len(bullet) >= 25 and bullet not in clean_bullets:
                clean_bullets.append(bullet)

        return clean_bullets

    def add_detected_skills(self, resume_json, resume_text):
        """
        Add obvious technical skills that appear in raw text but Qwen may miss.
        """

        text = resume_text.lower()
        skills = resume_json.get("skills", {})

        skill_map = {
            "programming_languages": [
                "Python",
                "SQL"
            ],
            "frameworks": [
                "Pandas",
                "NumPy",
                "Scikit-learn",
                "TensorFlow",
                "PyTorch",
                "Django",
                "Machine Learning",
                "Deep Learning",
                "Reinforcement Learning",
                "Feature Engineering",
                "EDA",
                "Data Cleaning",
                "Data Wrangling",
                "Statistical Analysis",
                "Predictive Modelling"
            ],
            "databases": [],
            "cloud": [],
            "tools": [
                "Power BI",
                "Tableau",
                "Excel",
                "Jupyter Notebook",
                "Git/GitHub",
                "Matplotlib",
                "Plotly",
                "Looker",
                "Yumpingo"
            ],
            "soft_skills": [
                "Leadership",
                "Communication",
                "Collaboration",
                "Problem Solving"
            ]
        }

        for category, skill_list in skill_map.items():

            skills.setdefault(category, [])

            for skill in skill_list:

                if skill.lower() in text:
                    self.add_unique(skills[category], skill)

    def add_unique(self, items, value):
        """
        Add value to list if it is not already present.
        """

        existing = [
            str(item).lower().strip()
            for item in items
        ]

        if value.lower().strip() not in existing:
            items.append(value)
            
    def remove_unsupported_skills(self, resume_json, resume_text):
        """
        Remove skills that Qwen invented from prompt examples.
        A skill should remain only if it appears clearly in the original resume text.
        """

        text = resume_text.lower()

        skills = resume_json.get("skills", {})

        for category, skill_list in skills.items():

            if not isinstance(skill_list, list):
                skills[category] = []
                continue

            cleaned_skills = []

            for skill in skill_list:

                if self.skill_exists_in_resume_text(skill, text):

                    existing = [
                        str(item).lower().strip()
                        for item in cleaned_skills
                    ]

                    if str(skill).lower().strip() not in existing:
                        cleaned_skills.append(skill)

            skills[category] = cleaned_skills


    def skill_exists_in_resume_text(self, skill, text):
        """
        Check whether a skill is genuinely supported by the original resume text.
        """

        if not skill:
            return False

        skill_text = str(skill).lower().strip()

        # Special case: R should not be matched from R², research, route, etc.
        if skill_text == "r":
            return (
                re.search(r"\br programming\b", text) is not None
                or re.search(r"\br language\b", text) is not None
                or re.search(r"programming languages?:.*\br\b", text) is not None
            )

        aliases = {
            "git": ["git", "github", "git/github"],
            "git/github": ["git", "github", "git/github"],
            "scikit-learn": ["scikit-learn", "sklearn"],
            "tensorflow": ["tensorflow"],
            "pytorch": ["pytorch"],
            "keras": ["keras"],
            "django": ["django"],
            "pandas": ["pandas"],
            "numpy": ["numpy"],
            "mysql": ["mysql"],
            "postgresql": ["postgresql"],
            "sqlite": ["sqlite"],
            "sql server": ["sql server", "mssql"],
            "machine learning": ["machine learning", "ml"],
            "deep learning": ["deep learning", "cnn"],
            "reinforcement learning": ["reinforcement learning", "ppo", "dqn", "ddqn"],
            "data science": ["data science"],
            "statistical analysis": ["statistical analysis"],
            "feature engineering": ["feature engineering"],
            "eda": ["eda", "exploratory data analysis"],
            "data cleaning": ["data cleaning"],
            "data wrangling": ["data wrangling"],
            "power bi": ["power bi"],
            "tableau": ["tableau"],
            "excel": ["excel"],
            "jupyter notebook": ["jupyter notebook", "jupyter"],
            "matplotlib": ["matplotlib"],
            "plotly": ["plotly"],
            "looker": ["looker"],
            "yumpingo": ["yumpingo"],
            "communication": ["communication", "communicator"],
            "leadership": ["leadership", "led"],
            "collaboration": ["collaboration", "collaborated"],
            "problem-solving": ["problem-solving", "problem solving"],
            "problem solving": ["problem-solving", "problem solving"]
        }

        check_terms = aliases.get(skill_text, [skill_text])

        for term in check_terms:

            term = term.lower().strip()

            if not term:
                continue

            pattern = r"(?<![a-zA-Z0-9])" + re.escape(term) + r"(?![a-zA-Z0-9])"

            if re.search(pattern, text):
                return True

        return False