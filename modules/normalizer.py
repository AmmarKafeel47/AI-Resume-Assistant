import re


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
    def normalize(skill: str) -> str:
        """
        Normalize a skill name for matching.
        """

        if not skill:
            return ""

        # Lowercase
        skill = skill.lower()

        # Remove extra spaces
        skill = skill.strip()

        # Replace multiple spaces with one
        skill = re.sub(r"\s+", " ", skill)

        # Apply known replacements
        skill = SkillNormalizer.REPLACEMENTS.get(skill, skill)

        return skill