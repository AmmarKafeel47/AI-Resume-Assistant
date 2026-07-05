import re

from services.ai.provider_factory import ProviderFactory
from modules.prompt_loader import PromptLoader
from modules.json_parser import JsonParser


class RecommendationEngine:

    def __init__(self):
        self.ai = ProviderFactory.get_provider()

    def generate(self, resume_json, jd_json, match_result):

        simplified_match = self.simplify_match_result(match_result)
        simplified_resume = self.simplify_resume(resume_json)
        simplified_jd = self.simplify_jd(jd_json)

        prompt = PromptLoader.load(
            "prompts/recommendation_prompt.txt",
            {
                "RESUME": simplified_resume,
                "JD": simplified_jd,
                "MATCH": simplified_match
            }
        )

        response = self.ai.generate(prompt)

        # Remove <think>...</think> if present
        response = re.sub(
            r"<think>.*?</think>",
            "",
            response,
            flags=re.DOTALL
        ).strip()

        # Extract only the JSON object
        match = re.search(r"\{.*\}", response, re.DOTALL)

        if match:
            response = match.group()

        try:
            parsed = JsonParser.parse(response)

            return self.ensure_recommendation_schema(
                parsed,
                simplified_match,
                simplified_jd
            )

        except Exception:

            return self.fallback_recommendations(
                simplified_match,
                simplified_jd
            )

    def simplify_match_result(self, match_result):
        """
        Keep only the fields Qwen needs for career advice.
        Do not send score_breakdown/category_scores because it is too large.
        """

        match_result = match_result or {}

        return {
            "match_score": match_result.get("match_score", 0),
            "matched_skills": match_result.get("matched_skills", []),
            "missing_skills": match_result.get("missing_skills", []),
            "required_matched": match_result.get("required_matched", []),
            "required_missing": match_result.get("required_missing", []),
            "preferred_matched": match_result.get("preferred_matched", []),
            "preferred_missing": match_result.get("preferred_missing", [])
        }

    def simplify_resume(self, resume_json):
        """
        Reduce resume JSON so Qwen gets enough context without overload.
        """

        resume_json = resume_json or {}

        return {
            "name": resume_json.get("personal_information", {}).get("name", ""),
            "headline": resume_json.get("headline", ""),
            "summary": resume_json.get("summary", ""),
            "skills": resume_json.get("skills", {}),
            "experience": [
                {
                    "job_title": exp.get("job_title", ""),
                    "company": exp.get("company", ""),
                    "responsibilities": exp.get("responsibilities", [])
                }
                for exp in resume_json.get("experience", [])
            ],
            "projects": [
                {
                    "title": project.get("title", ""),
                    "description": project.get("description", "")
                }
                for project in resume_json.get("projects", [])
            ]
        }

    def simplify_jd(self, jd_json):
        """
        Reduce JD JSON to only useful recommendation context.
        """

        jd_json = jd_json or {}

        return {
            "job_title": jd_json.get("job_title", ""),
            "company": jd_json.get("company", ""),
            "required_skills": jd_json.get("required_skills", []),
            "preferred_skills": jd_json.get("preferred_skills", []),
            "responsibilities": jd_json.get("responsibilities", [])
        }

    def ensure_recommendation_schema(self, parsed, match_result, jd_json):
        """
        Ensure UI always receives the expected keys.
        """

        if not isinstance(parsed, dict):
            return self.fallback_recommendations(match_result, jd_json)

        parsed.setdefault("executive_summary", "")
        parsed.setdefault("top_strengths", [])
        parsed.setdefault("critical_skill_gaps", [])
        parsed.setdefault("resume_improvements", [])
        parsed.setdefault("ats_keywords", [])
        parsed.setdefault("learning_recommendations", [])

        # If Qwen returns empty content, fill it using deterministic fallback
        if not parsed["executive_summary"]:
            parsed["executive_summary"] = self.build_summary(match_result, jd_json)

        if not parsed["top_strengths"]:
            parsed["top_strengths"] = match_result.get("matched_skills", [])[:5]

        if not parsed["critical_skill_gaps"]:
            parsed["critical_skill_gaps"] = self.build_skill_gaps(match_result)

        if not parsed["resume_improvements"]:
            parsed["resume_improvements"] = self.build_resume_improvements(match_result)

        if not parsed["ats_keywords"]:
            parsed["ats_keywords"] = self.build_ats_keywords(match_result)

        if not parsed["learning_recommendations"]:
            parsed["learning_recommendations"] = self.build_learning_recommendations(match_result)

        return parsed

    def fallback_recommendations(self, match_result, jd_json):
        """
        Fallback if Qwen fails completely.
        """

        return {
            "executive_summary": self.build_summary(match_result, jd_json),
            "top_strengths": match_result.get("matched_skills", [])[:5],
            "critical_skill_gaps": self.build_skill_gaps(match_result),
            "resume_improvements": self.build_resume_improvements(match_result),
            "ats_keywords": self.build_ats_keywords(match_result),
            "learning_recommendations": self.build_learning_recommendations(match_result)
        }

    def build_summary(self, match_result, jd_json):

        score = match_result.get("match_score", 0)
        job_title = jd_json.get("job_title", "this role")
        company = jd_json.get("company", "the company")

        matched = match_result.get("matched_skills", [])
        missing = match_result.get("missing_skills", [])

        matched_text = ", ".join(matched[:4]) if matched else "some relevant skills"
        missing_text = ", ".join(missing[:3]) if missing else "no major missing skills"

        return (
            f"The resume has a {score}% match for the {job_title} role at {company}. "
            f"The strongest alignment is in {matched_text}. "
            f"The main improvement areas are {missing_text}."
        )

    def build_skill_gaps(self, match_result):

        required_missing = match_result.get("required_missing", [])
        preferred_missing = match_result.get("preferred_missing", [])

        gaps = []

        for skill in required_missing[:5]:
            gaps.append({
                "skill_name": self.format_skill(skill),
                "recommendation": self.recommendation_for_skill(skill, required=True)
            })

        for skill in preferred_missing[:3]:
            if skill not in required_missing:
                gaps.append({
                    "skill_name": self.format_skill(skill),
                    "recommendation": self.recommendation_for_skill(skill, required=False)
                })

        return gaps

    def build_resume_improvements(self, match_result):

        improvements = []

        required_missing = match_result.get("required_missing", [])

        if required_missing:
            improvements.append({
                "improvement_point": "Strengthen alignment with required skills.",
                "recommendation": (
                    "Prioritize the missing required skills in learning or future projects. "
                    "Do not add them to the resume until you have genuine experience."
                )
            })

        improvements.append({
            "improvement_point": "Highlight matched strengths more clearly.",
            "recommendation": (
                "Emphasize existing matched skills such as Python, machine learning, "
                "data analysis, Git, and communication through project and experience bullets."
            )
        })

        return improvements

    def build_ats_keywords(self, match_result):

        keywords = []

        for skill in match_result.get("matched_skills", []):
            if skill not in keywords:
                keywords.append(skill)

        for skill in match_result.get("required_missing", []):
            if skill not in keywords:
                keywords.append(skill)

        return keywords[:8]

    def build_learning_recommendations(self, match_result):

        recommendations = []

        missing = (
            match_result.get("required_missing", [])
            + match_result.get("preferred_missing", [])
        )

        for skill in missing[:4]:
            recommendations.append(
                self.learning_recommendation_for_skill(skill)
            )

        return recommendations

    def recommendation_for_skill(self, skill, required=True):

        skill = str(skill).lower()

        priority = "required" if required else "preferred"

        if skill == "cloud":
            return f"Gain hands-on cloud experience through a small GCP, AWS, or Azure project because this is a {priority} gap."

        if skill == "mlops":
            return f"Learn model deployment, monitoring, and production ML workflows because this is a {priority} gap."

        if skill == "software engineering":
            return f"Strengthen software engineering practices such as testing, clean code, and object-oriented programming because this is a {priority} gap."

        if skill == "llms":
            return f"Build a small LLM-based project before adding LLM experience to the resume."

        if skill == "retail analytics":
            return f"Study retail analytics use cases such as pricing, demand forecasting, and inventory optimisation."

        return f"Develop practical experience in {skill} before adding it to the resume."

    def learning_recommendation_for_skill(self, skill):

        skill = str(skill).lower()

        if skill == "cloud":
            return "Build and deploy a small Python ML project on GCP, AWS, or Azure."

        if skill == "mlops":
            return "Learn basic MLOps: model deployment, monitoring, versioning, and reproducible pipelines."

        if skill == "software engineering":
            return "Practice unit testing, object-oriented programming, clean code, and Git workflows."

        if skill == "llms":
            return "Create a small LLM application using a local or API-based model and document it on GitHub."

        if skill == "retail analytics":
            return "Build a retail analytics mini-project using demand forecasting or price optimisation data."

        return f"Practice {skill} through a small portfolio project."

    def format_skill(self, skill):

        special = {
            "mlops": "MLOps",
            "llms": "LLMs",
            "sql": "SQL",
            "git": "Git",
            "cloud": "Cloud",
            "python": "Python"
        }

        skill = str(skill).strip()

        return special.get(skill.lower(), skill.title())