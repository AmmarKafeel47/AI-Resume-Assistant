import re
from modules.skill_dictionary import canonical_skill

class SkillNormalizer:

    REPLACEMENTS = {
        "scikit learn": "scikit-learn",
        "scikitlearn": "scikit-learn",
        "powerbi": "power bi",
        "google collab": "google colab",
        "google colaboratory": "google colab",
        "js": "javascript",
        "nodejs": "node.js",
        "tf": "tensorflow",
        "py torch": "pytorch",
    }

    @staticmethod
    def normalize(skill) -> str:
        """
        Normalize a skill name for ATS matching.
        """

        if not skill:
            return ""

        if not isinstance(skill, str):
            skill = str(skill)

        # Lowercase
        skill = skill.lower()

        # Remove leading/trailing spaces
        skill = skill.strip()

        # Replace multiple spaces
        skill = re.sub(r"\s+", " ", skill)

        # Apply known replacements
        skill = SkillNormalizer.REPLACEMENTS.get(skill, skill)

        # Convert to canonical skill
        skill = canonical_skill(skill)

        return skill