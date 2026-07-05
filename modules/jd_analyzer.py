import json
import re

from services.ai.provider_factory import ProviderFactory
from modules.prompt_loader import PromptLoader


class JDAnalyzer:

    def __init__(self):
        self.ai = ProviderFactory.get_provider()

    def analyze(self, job_description):

        prompt = PromptLoader.load(
            "prompts/analyze_jd.txt",
            {
                "JOB_DESCRIPTION": job_description
            }
        )

        response = self.ai.generate(prompt)

        jd_json = self.parse_json_response(response)

        if not isinstance(jd_json, dict):
            jd_json = self.empty_schema()

        jd_json = self.clean_jd_json(jd_json, job_description)

        return jd_json

    def parse_json_response(self, response):
        """
        Parse Qwen JSON response safely.
        """

        if isinstance(response, dict):
            return response

        if not response:
            return None

        text = str(response).strip()
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

        try:
            return json.loads(text)

        except json.JSONDecodeError:
            pass

        extracted = self.extract_json_object(text)

        if extracted:
            try:
                return json.loads(extracted)
            except json.JSONDecodeError:
                return None

        return None

    def extract_json_object(self, text):
        """
        Extract first valid JSON object from a messy AI response.
        """

        start = text.find("{")

        if start == -1:
            return None

        brace_count = 0
        in_string = False
        escape = False

        for index in range(start, len(text)):

            char = text[index]

            if escape:
                escape = False
                continue

            if char == "\\":
                escape = True
                continue

            if char == '"':
                in_string = not in_string
                continue

            if not in_string:

                if char == "{":
                    brace_count += 1

                elif char == "}":
                    brace_count -= 1

                    if brace_count == 0:
                        return text[start:index + 1]

        return None

    def empty_schema(self):
        """
        Default JD schema.
        """

        return {
            "job_title": "",
            "company": "",
            "required_skills": [],
            "preferred_skills": [],
            "responsibilities": [],
            "qualifications": [],
            "experience_required": "",
            "education_required": "",
            "tools": [],
            "frameworks": [],
            "cloud": [],
            "databases": [],
            "programming_languages": [],
            "soft_skills": []
        }

    def clean_jd_json(self, jd_json, job_description):
        """
        Improve JD extraction using deterministic Python rules.
        This prevents Qwen from missing obvious required skills.
        """

        self.ensure_schema(jd_json)

        text = job_description or ""
        text_lower = text.lower()

        required_text = self.extract_section(
            text,
            start_markers=[
                "required skills",
                "requirements",
                "essential"
            ],
            end_markers=[
                "nice to have",
                "desirable",
                "preferred",
                "benefits",
                "location",
                "start date"
            ]
        )

        preferred_text = self.extract_section(
            text,
            start_markers=[
                "nice to have",
                "desirable",
                "preferred"
            ],
            end_markers=[
                "benefits",
                "location",
                "start date"
            ]
        )

        if not required_text:
            required_text = text

        # Required skills
        required_rules = {
            "Python": [
                "python"
            ],
            "Machine Learning": [
                "machine learning",
                "predictive machine learning",
                "predictive modelling",
                "predictive modeling",
                "machine learning models"
            ],
            "Data Analysis": [
                "analyse client data",
                "analyze client data",
                "data analysis",
                "actionable insights",
                "mathematical techniques",
                "modelling frameworks",
                "modeling frameworks",
                "statistical"
            ],
            "Communication": [
                "communication skills",
                "explain models",
                "technical and non-technical stakeholders",
                "non-technical stakeholders"
            ],
            "MLOps": [
                "deploying and maintaining",
                "production environments",
                "models in production",
                "model deployment"
            ],
            "Git": [
                "git"
            ],
            "Cloud": [
                "cloud computing platform",
                "cloud platform",
                "cloud platforms",
                "gcp",
                "aws",
                "azure"
            ],
            "Software Engineering": [
                "software engineering",
                "unit testing",
                "object-oriented programming",
                "production-quality code",
                "clean code"
            ]
        }

        for skill, keywords in required_rules.items():
            if self.contains_any(required_text, keywords):
                self.add_unique(jd_json["required_skills"], skill)

        # Preferred skills
        preferred_rules = {
            "SQL": [
                "sql"
            ],
            "LLMs": [
                "llm",
                "llms",
                "large language model",
                "large language models"
            ],
            "Retail Analytics": [
                "retail",
                "consumer goods",
                "price optimisation",
                "price optimization",
                "demand forecasting",
                "inventory optimisation",
                "inventory optimization"
            ]
        }

        for skill, keywords in preferred_rules.items():
            if self.contains_any(preferred_text, keywords):
                self.add_unique(jd_json["preferred_skills"], skill)

        # Structured fields from full JD
        if "python" in text_lower:
            self.add_unique(jd_json["programming_languages"], "Python")

        if re.search(r"\bR\b", text):
            self.add_unique(jd_json["programming_languages"], "R")

        framework_rules = {
            "Scikit-learn": ["scikit-learn", "sklearn"],
            "Pandas": ["pandas"],
            "NumPy": ["numpy"],
            "TensorFlow": ["tensorflow"],
            "PyTorch": ["pytorch"],
            "Keras": ["keras"]
        }

        for framework, keywords in framework_rules.items():
            if self.contains_any(text, keywords):
                self.add_unique(jd_json["frameworks"], framework)

        tool_rules = {
            "Git": ["git"],
            "Unit Testing": ["unit testing"],
            "LLMs": ["llm", "llms", "large language model", "large language models"]
        }

        for tool, keywords in tool_rules.items():
            if self.contains_any(text, keywords):
                self.add_unique(jd_json["tools"], tool)

        cloud_rules = {
            "GCP": ["gcp", "google cloud"],
            "AWS": ["aws"],
            "Azure": ["azure"],
            "Cloud Computing Platform": [
                "cloud computing platform",
                "cloud platform",
                "cloud platforms"
            ]
        }

        for cloud, keywords in cloud_rules.items():
            if self.contains_any(text, keywords):
                self.add_unique(jd_json["cloud"], cloud)

        if "sql" in text_lower:
            self.add_unique(jd_json["databases"], "SQL")

        if "relational database" in text_lower or "relational databases" in text_lower:
            self.add_unique(jd_json["databases"], "Relational Databases")

        soft_skill_rules = {
            "Communication": [
                "communication skills",
                "communicate",
                "explain models",
                "technical and non-technical stakeholders"
            ],
            "Collaboration": [
                "collaborate",
                "collaboration",
                "working with"
            ],
            "Commercial Awareness": [
                "commercial",
                "commercially minded"
            ]
        }

        for skill, keywords in soft_skill_rules.items():
            if self.contains_any(text, keywords):
                self.add_unique(jd_json["soft_skills"], skill)

        self.recover_responsibilities(jd_json, text)
        self.remove_invented_requirements(jd_json, text)
        
        self.remove_invalid_items(jd_json)

        return jd_json

    def ensure_schema(self, jd_json):
        """
        Ensure all expected keys exist.
        """

        defaults = self.empty_schema()

        for key, value in defaults.items():
            jd_json.setdefault(key, value)

        list_keys = [
            "required_skills",
            "preferred_skills",
            "responsibilities",
            "qualifications",
            "tools",
            "frameworks",
            "cloud",
            "databases",
            "programming_languages",
            "soft_skills"
        ]

        for key in list_keys:
            if not isinstance(jd_json.get(key), list):
                jd_json[key] = []

    def extract_section(self, text, start_markers, end_markers):
        """
        Extract a JD section between headings.
        """

        text_lower = text.lower()

        start_index = -1

        for marker in start_markers:

            position = text_lower.find(marker.lower())

            if position != -1:
                start_index = position
                break

        if start_index == -1:
            return ""

        end_index = len(text)

        for marker in end_markers:

            position = text_lower.find(marker.lower(), start_index + 1)

            if position != -1:
                end_index = min(end_index, position)

        return text[start_index:end_index]

    def contains_any(self, text, keywords):
        """
        Check whether any keyword appears in text.
        """

        text_lower = text.lower()

        for keyword in keywords:

            if keyword.lower() in text_lower:
                return True

        return False

    def remove_invalid_items(self, jd_json):
        """
        Remove empty values and nested dicts from list fields.
        """

        list_keys = [
            "required_skills",
            "preferred_skills",
            "responsibilities",
            "qualifications",
            "tools",
            "frameworks",
            "cloud",
            "databases",
            "programming_languages",
            "soft_skills"
        ]

        for key in list_keys:

            cleaned = []

            for item in jd_json.get(key, []):

                if isinstance(item, dict):
                    continue

                item = str(item).strip()

                if not item:
                    continue

                self.add_unique(cleaned, item)

            jd_json[key] = cleaned
            
            
    def recover_responsibilities(self, jd_json, job_description):
        """
        Recover responsibilities from the Responsibilities section if Qwen misses them.
        """

        if jd_json.get("responsibilities"):
            return

        responsibilities_text = self.extract_section(
            job_description,
            start_markers=[
                "responsibilities",
                "the role"
            ],
            end_markers=[
                "required skills",
                "requirements",
                "nice to have",
                "desirable",
                "benefits",
                "location",
                "start date"
            ]
        )

        if not responsibilities_text:
            return

        lines = [
            line.strip()
            for line in responsibilities_text.splitlines()
            if line.strip()
        ]

        responsibility_lines = []

        action_words = [
            "owning",
            "design",
            "develop",
            "test",
            "evaluate",
            "improve",
            "analyse",
            "analyze",
            "build",
            "stay",
            "work",
            "collaborate",
            "deliver"
        ]

        for line in lines:

            line_lower = line.lower()

            if line_lower.startswith("responsibilities"):
                continue

            if len(line) < 25:
                continue

            if any(line_lower.startswith(word) for word in action_words):
                responsibility_lines.append(line)

        jd_json["responsibilities"] = responsibility_lines[:8]


    def remove_invented_requirements(self, jd_json, job_description):
        """
        Remove education or experience requirements if they do not appear in the JD.
        """

        text = job_description.lower()

        # Remove invented education requirements
        education_terms = [
            "bachelor",
            "master",
            "msc",
            "bsc",
            "degree",
            "phd",
            "computer science",
            "mathematics",
            "statistics"
        ]

        if not any(term in text for term in education_terms):
            jd_json["qualifications"] = []
            jd_json["education_required"] = ""

        # Remove invented years of experience
        explicit_years_pattern = r"\b\d+\+?\s*(years|yrs)\b"

        if not re.search(explicit_years_pattern, text):
            jd_json["experience_required"] = ""

    def add_unique(self, items, value):
        """
        Add a value only once.
        """

        value = str(value).strip()

        if not value:
            return

        existing = [
            str(item).lower().strip()
            for item in items
        ]

        if value.lower() not in existing:
            items.append(value)