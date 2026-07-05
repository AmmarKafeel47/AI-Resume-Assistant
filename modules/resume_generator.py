from copy import deepcopy
import re
from services.ai.provider_factory import ProviderFactory
from modules.prompt_loader import PromptLoader
from utils.json_validator import JSONValidator


class ResumeGenerator:

    def __init__(self):
        self.ai = ProviderFactory.get_provider()

    def generate(
        self,
        resume_json,
        jd_json,
        match_result,
        recommendations
    ):

        prompt = PromptLoader.load(
            "prompts/tailored_resume.txt",
            {
                "RESUME": resume_json,
                "JD": jd_json,
                "MATCH": match_result,
                "RECOMMENDATIONS": recommendations
            }
        )

        response = self.ai.generate(prompt)

        valid, parsed = JSONValidator.validate(response)

        if not valid:
            return parsed

        # Safety layer: prevent AI hallucinations from reaching DOCX export
        safe_resume = self.safe_merge_with_original(parsed, resume_json)

        return safe_resume

    def safe_merge_with_original(self, generated_resume, original_resume):
        """
        Keep the AI-generated summary if safe, but preserve factual resume sections
        from the original resume so Qwen cannot invent skills, dates, certifications,
        projects, companies, or achievements.
        """

        original = deepcopy(original_resume or {})
        generated = generated_resume if isinstance(generated_resume, dict) else {}

        self.ensure_resume_schema(original)

        safe_resume = deepcopy(original)

        # Keep original factual identity fields
        safe_resume["personal_information"] = deepcopy(
            original.get("personal_information", {})
        )

        # Keep original headline to avoid invented seniority
        safe_resume["headline"] = str(original.get("headline") or "").strip()

        # Allow AI summary only after removing unsafe invented cloud wording
        generated_summary = str(generated.get("summary") or "").strip()

        if generated_summary:
            safe_resume["summary"] = self.clean_generated_summary(
                generated_summary,
                original
            )
        else:
            safe_resume["summary"] = str(original.get("summary") or "").strip()

        # Keep original factual sections
        #safe_resume["skills"] = deepcopy(original.get("skills", {}))
        safe_resume["skills"] = self.clean_safe_skills(
            deepcopy(original.get("skills", {}))
        )
        safe_resume["experience"] = deepcopy(original.get("experience", []))
        safe_resume["projects"] = deepcopy(original.get("projects", []))
        safe_resume["education"] = deepcopy(original.get("education", []))
        safe_resume["certifications"] = deepcopy(original.get("certifications", []))
        safe_resume["languages"] = deepcopy(original.get("languages", []))

        # Remove all None values so exporter does not crash
        safe_resume = self.replace_none_values(safe_resume)

        self.ensure_resume_schema(safe_resume)

        return safe_resume
    
    def clean_safe_skills(self, skills):
        """
        Remove known hallucinated skills that should not be exported
        unless they genuinely exist in the original resume.
        """

        blocked_skills = {
            "r",
            "keras",
            "mysql",
            "postgresql",
            "sqlite",
            "sql server",
            "mssql",
            "aws",
            "azure",
            "gcp",
            "google cloud",
            "cloud computing",
            "cloud computing platform"
        }

        cleaned = {}

        for category, skill_list in skills.items():

            if not isinstance(skill_list, list):
                cleaned[category] = []
                continue

            cleaned_list = []

            for skill in skill_list:

                skill_text = str(skill).lower().strip()

                if skill_text in blocked_skills:
                    continue

                if skill_text not in [str(item).lower().strip() for item in cleaned_list]:
                    cleaned_list.append(skill)

            cleaned[category] = cleaned_list

        cleaned.setdefault("programming_languages", [])
        cleaned.setdefault("frameworks", [])
        cleaned.setdefault("databases", [])
        cleaned.setdefault("cloud", [])
        cleaned.setdefault("tools", [])
        cleaned.setdefault("soft_skills", [])

        return cleaned

    def clean_generated_summary(self, summary, original_resume):
        """
        Remove unsafe invented terms from AI summary.
        If the summary still contains hallucinated claims, fall back to the original summary.
        """

        skills = original_resume.get("skills", {}) if isinstance(original_resume, dict) else {}
        original_text = str(original_resume).lower()

        original_cloud_skills = skills.get("cloud", [])

        original_has_cloud = (
            isinstance(original_cloud_skills, list)
            and len(original_cloud_skills) > 0
        )

        if not original_has_cloud:

            unsafe_cloud_phrases = [
                r"experienced in deploying machine learning models using gcp for production environments\.?",
                r"experienced in deploying machine learning models using aws for production environments\.?",
                r"experienced in deploying machine learning models using azure for production environments\.?",
                r"experienced in deploying machine learning models using cloud platforms?\.?",
                r"proficient in cloud technologies",
                r"proficient in cloud computing",
                r"skilled in cloud technologies",
                r"skilled in cloud computing",
                r"cloud technologies",
                r"cloud computing",
                r"cloud platforms?",
                r"using gcp",
                r"using aws",
                r"using azure",
                r"\(gcp or other\)",
                r"\(aws or other\)",
                r"\(azure or other\)"
            ]

            for phrase in unsafe_cloud_phrases:
                summary = re.sub(
                    phrase,
                    "",
                    summary,
                    flags=re.IGNORECASE
                )

            summary = re.sub(
                r"\bGCP\b|\bAWS\b|\bAzure\b|\bGoogle Cloud\b",
                "",
                summary,
                flags=re.IGNORECASE
            )

        # Remove production-deployment claims unless clearly present in original resume
        original_has_production_deployment = (
            "production environment" in original_text
            or "production environments" in original_text
            or "deployed solutions" in original_text
            or "mlops" in original_text
        )

        if not original_has_production_deployment:

            unsafe_deployment_phrases = [
                r"strong communicator skilled in production environment deployment of machine learning models\.?",
                r"skilled in production environment deployment of machine learning models\.?",
                r"production environment deployment of machine learning models",
                r"production deployment of machine learning models",
                r"deploying machine learning models in production environments",
                r"machine learning models in production environments",
                r"production environments"
            ]

            for phrase in unsafe_deployment_phrases:
                summary = re.sub(
                    phrase,
                    "",
                    summary,
                    flags=re.IGNORECASE
                )

        # Soften exaggerated wording
        summary = re.sub(
            r"^expert in",
            "Skilled in",
            summary,
            flags=re.IGNORECASE
        )

        # Remove project management if original resume does not contain it
        if "project management" not in original_text:
            summary = re.sub(
                r"\bproject management\b",
                "",
                summary,
                flags=re.IGNORECASE
            )

        # Clean empty brackets and awkward leftovers
        summary = re.sub(r"\(\s*\)", "", summary)
        summary = re.sub(r"\[\s*\]", "", summary)

        # Clean broken connector phrases
        summary = re.sub(r",\s*and\s*\.", ".", summary)
        summary = re.sub(r",\s*and\s*,", ",", summary)
        summary = re.sub(r"\band\s*\.", ".", summary)
        summary = re.sub(r"\band\s*,", "", summary)

        # Clean repeated punctuation and spacing
        summary = re.sub(r"\s+", " ", summary).strip()
        summary = summary.replace(" ,", ",")
        summary = summary.replace(" .", ".")
        summary = summary.replace("..", ".")
        summary = summary.replace(",.", ".")
        summary = summary.strip(" ,;")

        # If cleanup made it awkward or too short, use original summary
        bad_leftovers = [
            "()",
            "cloud",
            "gcp",
            "aws",
            "azure",
            "production environment",
            "production deployment"
        ]

        if not original_has_cloud:
            if any(term in summary.lower() for term in ["cloud", "gcp", "aws", "azure"]):
                return str(original_resume.get("summary") or "").strip()

        if not original_has_production_deployment:
            if any(term in summary.lower() for term in ["production environment", "production deployment"]):
                return str(original_resume.get("summary") or "").strip()

        if len(summary) < 80:
            return str(original_resume.get("summary") or "").strip()

        return summary
    
    
    def ensure_resume_schema(self, resume):
        """
        Ensure required resume keys exist.
        """

        resume.setdefault("personal_information", {})
        resume.setdefault("headline", "")
        resume.setdefault("summary", "")
        resume.setdefault("skills", {})
        resume.setdefault("experience", [])
        resume.setdefault("projects", [])
        resume.setdefault("education", [])
        resume.setdefault("certifications", [])
        resume.setdefault("languages", [])

        personal = resume["personal_information"]
        personal.setdefault("name", "")
        personal.setdefault("email", "")
        personal.setdefault("phone", "")
        personal.setdefault("linkedin", "")
        personal.setdefault("github", "")

        skills = resume["skills"]
        skills.setdefault("programming_languages", [])
        skills.setdefault("frameworks", [])
        skills.setdefault("databases", [])
        skills.setdefault("cloud", [])
        skills.setdefault("tools", [])
        skills.setdefault("soft_skills", [])

    def replace_none_values(self, value):
        """
        Recursively replace None with empty string.
        """

        if value is None:
            return ""

        if isinstance(value, dict):
            return {
                key: self.replace_none_values(item)
                for key, item in value.items()
            }

        if isinstance(value, list):
            return [
                self.replace_none_values(item)
                for item in value
            ]

        return value