from modules.normalizer import SkillNormalizer
from modules.skill_dictionary import get_skill_category


class ResumeMatcher:

    PREFERRED_MULTIPLIER = 0.4

    SKILL_WEIGHTS = {
        # Programming
        "python": 20,
        "sql": 12,
        "r": 10,

        # ML / AI
        "machine learning": 25,
        "deep learning": 18,
        "reinforcement learning": 14,

        # Data
        "data analysis": 18,
        "data visualization": 12,

        # Cloud / Deployment
        "cloud": 18,
        "mlops": 16,

        # Engineering
        "software engineering": 14,
        "unit testing": 6,

        # Tools
        "git": 8,
        "excel": 5,
        "jupyter notebook": 5,
        "web development": 5,

        # LLM / Domain
        "llms": 6,
        "retail analytics": 5,
        "commercial awareness": 4,

        # Soft skills
        "communication": 8
    }

    CATEGORY_DEFAULT_WEIGHTS = {
        "Programming Languages": 15,
        "Machine Learning": 18,
        "Data Analysis": 14,
        "Data Visualization": 10,
        "Cloud": 18,
        "MLOps": 16,
        "Version Control": 8,
        "Soft Skills": 6,
        "Web Development": 5,
        "Other": 4
    }

    def __init__(self, resume_json, jd_json):
        self.resume = resume_json or {}
        self.jd = jd_json or {}

    def match(self):
        resume_skills = self.flatten_resume_skills()
        required_skills, preferred_skills = self.flatten_jd_skills_by_priority()

        required_matched = sorted(resume_skills.intersection(required_skills))
        required_missing = sorted(required_skills.difference(resume_skills))

        preferred_matched = sorted(resume_skills.intersection(preferred_skills))
        preferred_missing = sorted(preferred_skills.difference(resume_skills))

        matched = sorted(set(required_matched + preferred_matched))
        missing = sorted(set(required_missing + preferred_missing))

        score_details = self.calculate_weighted_score(
            required_matched,
            required_missing,
            preferred_matched,
            preferred_missing
        )

        return {
            "match_score": score_details["overall_score"],
            "matched_skills": matched,
            "missing_skills": missing,
            "required_skills": sorted(required_skills),
            "preferred_skills": sorted(preferred_skills),
            "required_matched": required_matched,
            "required_missing": required_missing,
            "preferred_matched": preferred_matched,
            "preferred_missing": preferred_missing,
            "category_breakdown": self.category_breakdown(matched, missing),
            "score_breakdown": score_details
        }

    def extract_skills(self, value, skills):
        """
        Recursively extract skills from strings, lists and dictionaries.
        """

        if value is None:
            return

        if isinstance(value, str):

            normalized = SkillNormalizer.normalize(value)

            if normalized:
                skills.add(normalized)

        elif isinstance(value, list):

            for item in value:
                self.extract_skills(item, skills)

        elif isinstance(value, dict):

            for item in value.values():
                self.extract_skills(item, skills)

        else:

            normalized = SkillNormalizer.normalize(value)

            if normalized:
                skills.add(normalized)

    def flatten_resume_skills(self):
        """
        Extract normalized skills from resume JSON.
        """

        skills = set()

        self.extract_skills(self.resume.get("skills", {}), skills)

        for exp in self.resume.get("experience", []):
            self.extract_skills(exp.get("technologies", []), skills)

        for project in self.resume.get("projects", []):
            self.extract_skills(project.get("technologies", []), skills)
            self.extract_skills(project.get("skills_demonstrated", []), skills)

        return {skill for skill in skills if skill}

    def flatten_jd_skills_by_priority(self):
        """
        Extract required and preferred JD skills separately.

        We use required_skills and preferred_skills as the primary scoring source.
        Structured fields like tools/cloud/frameworks are only used as fallback
        if Qwen fails to extract required skills.
        """

        required_skills = set()
        preferred_skills = set()

        self.extract_skills(self.jd.get("required_skills", []), required_skills)
        self.extract_skills(self.jd.get("preferred_skills", []), preferred_skills)

        # Fallback only: if required_skills is empty, use structured fields
        if not required_skills:

            fallback_fields = [
                "programming_languages",
                "frameworks",
                "tools",
                "cloud",
                "databases",
                "soft_skills"
            ]

            for field in fallback_fields:
                self.extract_skills(self.jd.get(field, []), required_skills)

        required_skills = self.remove_noise(required_skills)
        preferred_skills = self.remove_noise(preferred_skills)

        # Avoid counting the same skill as both required and preferred
        preferred_skills = preferred_skills.difference(required_skills)

        return required_skills, preferred_skills

    def remove_noise(self, skills):
        """
        Remove overly vague items that should not be scored as ATS skills.
        """

        noise_terms = {
            "",
            "none",
            "not specified",
            "n/a"
        }

        return {
            skill
            for skill in skills
            if skill and skill not in noise_terms
        }

    def get_skill_weight(self, skill):
        """
        Return importance weight for a skill.
        """

        skill = SkillNormalizer.normalize(skill)

        if skill in self.SKILL_WEIGHTS:
            return self.SKILL_WEIGHTS[skill]

        category = get_skill_category(skill)

        return self.CATEGORY_DEFAULT_WEIGHTS.get(category, 4)

    def calculate_weighted_score(
        self,
        required_matched,
        required_missing,
        preferred_matched,
        preferred_missing
    ):
        """
        Calculate weighted ATS score.

        Required skills receive full weight.
        Preferred skills receive reduced weight.
        """

        required_matched_weight = sum(
            self.get_skill_weight(skill)
            for skill in required_matched
        )

        required_missing_weight = sum(
            self.get_skill_weight(skill)
            for skill in required_missing
        )

        preferred_matched_weight = sum(
            self.get_skill_weight(skill)
            for skill in preferred_matched
        ) * self.PREFERRED_MULTIPLIER

        preferred_missing_weight = sum(
            self.get_skill_weight(skill)
            for skill in preferred_missing
        ) * self.PREFERRED_MULTIPLIER

        matched_weight = required_matched_weight + preferred_matched_weight
        missing_weight = required_missing_weight + preferred_missing_weight
        total_weight = matched_weight + missing_weight

        if total_weight == 0:
            overall_score = 0
        else:
            overall_score = round((matched_weight / total_weight) * 100)

        required_score = self.calculate_simple_weighted_score(
            required_matched,
            required_missing
        )

        preferred_score = self.calculate_simple_weighted_score(
            preferred_matched,
            preferred_missing
        )

        all_skills = (
            required_matched
            + required_missing
            + preferred_matched
            + preferred_missing
        )

        return {
            "overall_score": overall_score,
            "required_score": required_score,
            "preferred_score": preferred_score,
            "matched_weight": round(matched_weight, 2),
            "missing_weight": round(missing_weight, 2),
            "total_weight": round(total_weight, 2),
            "required_matched_weight": round(required_matched_weight, 2),
            "required_missing_weight": round(required_missing_weight, 2),
            "preferred_matched_weight": round(preferred_matched_weight, 2),
            "preferred_missing_weight": round(preferred_missing_weight, 2),
            "skill_weights": {
                skill: self.get_skill_weight(skill)
                for skill in sorted(set(all_skills))
            },
            "priority_weights": {
                "required_multiplier": 1.0,
                "preferred_multiplier": self.PREFERRED_MULTIPLIER
            },
            "category_scores": self.category_score_breakdown(
                required_matched,
                required_missing,
                preferred_matched,
                preferred_missing
            )
        }

    def calculate_simple_weighted_score(self, matched, missing):
        """
        Calculate separate score for required or preferred skills.
        """

        matched_weight = sum(
            self.get_skill_weight(skill)
            for skill in matched
        )

        missing_weight = sum(
            self.get_skill_weight(skill)
            for skill in missing
        )

        total = matched_weight + missing_weight

        if total == 0:
            return 0

        return round((matched_weight / total) * 100)

    def category_breakdown(self, matched, missing):
        """
        Group matched and missing skills by category.
        """

        breakdown = {}

        for skill in matched:

            category = get_skill_category(skill)

            breakdown.setdefault(
                category,
                {
                    "matched": [],
                    "missing": []
                }
            )

            breakdown[category]["matched"].append(skill)

        for skill in missing:

            category = get_skill_category(skill)

            breakdown.setdefault(
                category,
                {
                    "matched": [],
                    "missing": []
                }
            )

            breakdown[category]["missing"].append(skill)

        return breakdown

    def category_score_breakdown(
        self,
        required_matched,
        required_missing,
        preferred_matched,
        preferred_missing
    ):
        """
        Calculate weighted category score.
        Required skills have full weight.
        Preferred skills have reduced weight.
        """

        category_scores = {}

        for skill in required_matched:
            self.add_category_score_item(
                category_scores,
                skill,
                status="matched",
                multiplier=1.0,
                priority="required"
            )

        for skill in required_missing:
            self.add_category_score_item(
                category_scores,
                skill,
                status="missing",
                multiplier=1.0,
                priority="required"
            )

        for skill in preferred_matched:
            self.add_category_score_item(
                category_scores,
                skill,
                status="matched",
                multiplier=self.PREFERRED_MULTIPLIER,
                priority="preferred"
            )

        for skill in preferred_missing:
            self.add_category_score_item(
                category_scores,
                skill,
                status="missing",
                multiplier=self.PREFERRED_MULTIPLIER,
                priority="preferred"
            )

        for category, data in category_scores.items():

            total = data["total_weight"]
            matched_weight = data["matched_weight"]

            if total == 0:
                data["score"] = 0
            else:
                data["score"] = round((matched_weight / total) * 100)

            data["matched_weight"] = round(data["matched_weight"], 2)
            data["missing_weight"] = round(data["missing_weight"], 2)
            data["total_weight"] = round(data["total_weight"], 2)

        return category_scores

    def add_category_score_item(
        self,
        category_scores,
        skill,
        status,
        multiplier,
        priority
    ):
        """
        Add a skill into category score breakdown.
        """

        category = get_skill_category(skill)
        weight = self.get_skill_weight(skill) * multiplier

        category_scores.setdefault(
            category,
            {
                "score": 0,
                "matched_weight": 0,
                "missing_weight": 0,
                "total_weight": 0,
                "matched": [],
                "missing": [],
                "required_matched": [],
                "required_missing": [],
                "preferred_matched": [],
                "preferred_missing": []
            }
        )

        category_scores[category]["total_weight"] += weight

        if status == "matched":

            category_scores[category]["matched_weight"] += weight
            category_scores[category]["matched"].append(skill)

            if priority == "required":
                category_scores[category]["required_matched"].append(skill)
            else:
                category_scores[category]["preferred_matched"].append(skill)

        else:

            category_scores[category]["missing_weight"] += weight
            category_scores[category]["missing"].append(skill)

            if priority == "required":
                category_scores[category]["required_missing"].append(skill)
            else:
                category_scores[category]["preferred_missing"].append(skill)