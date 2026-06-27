from modules.normalizer import SkillNormalizer


class ResumeMatcher:

    def __init__(self, resume_json, jd_json):
        self.resume = resume_json
        self.jd = jd_json

    def match(self):

        resume_skills = self.flatten_resume_skills()

        jd_skills = self.flatten_jd_skills()

        matched, missing = self.compare_skills()

        score = self.calculate_score(
            matched,
            jd_skills
        )

        return {
            "match_score": score,
            "matched_skills": matched,
            "missing_skills": missing
        }
        
    
    
    #Flatten Resume Skills
    def flatten_resume_skills(self):

        skills = set()

        resume_skills = self.resume.get("skills", {})

        # Main Skills
        for category in resume_skills.values():

            for skill in category:

                skills.add(
                    SkillNormalizer.normalize(skill)
                )

        # Experience Technologies
        for exp in self.resume.get("experience", []):

            for tech in exp.get("technologies", []):

                skills.add(
                    SkillNormalizer.normalize(tech)
                )

        # Project Technologies
        for project in self.resume.get("projects", []):

            for tech in project.get("technologies", []):

                skills.add(
                    SkillNormalizer.normalize(tech)
                )

            for skill in project.get("skills_demonstrated", []):

                skills.add(
                    SkillNormalizer.normalize(skill)
                )

        return skills
    
    #flatten job description skills
    
    def flatten_jd_skills(self):

        skills = set()

        # Required Skills
        for item in self.jd.get("required_skills", []):

            if isinstance(item, str):
                skills.add(
                    SkillNormalizer.normalize(item)
                )

            elif isinstance(item, dict):
                for value in item.values():
                    skills.add(
                        SkillNormalizer.normalize(value)
                    )

        # Programming Languages
        for skill in self.jd.get("programming_languages", []):

            if isinstance(skill, str):
                skills.add(
                    SkillNormalizer.normalize(skill)
                )

            elif isinstance(skill, dict):
                for value in skill.values():
                    skills.add(
                        SkillNormalizer.normalize(value)
                    )

        # Frameworks
        for skill in self.jd.get("frameworks", []):

            if isinstance(skill, str):
                skills.add(
                    SkillNormalizer.normalize(skill)
                )

            elif isinstance(skill, dict):
                for value in skill.values():
                    skills.add(
                        SkillNormalizer.normalize(value)
                    )

        # Tools
        for skill in self.jd.get("tools", []):

            if isinstance(skill, str):
                skills.add(
                    SkillNormalizer.normalize(skill)
                )

            elif isinstance(skill, dict):
                for value in skill.values():
                    skills.add(
                        SkillNormalizer.normalize(value)
                    )

        # Cloud
        for skill in self.jd.get("cloud", []):

            if isinstance(skill, str):
                skills.add(
                    SkillNormalizer.normalize(skill)
                )

            elif isinstance(skill, dict):
                for value in skill.values():
                    skills.add(
                        SkillNormalizer.normalize(value)
                    )

        # Databases
        for skill in self.jd.get("databases", []):

            if isinstance(skill, str):
                skills.add(
                    SkillNormalizer.normalize(skill)
                )

            elif isinstance(skill, dict):
                for value in skill.values():
                    skills.add(
                        SkillNormalizer.normalize(value)
                    )

        return skills


    def compare_skills(self):

        resume = self.flatten_resume_skills()

        jd = self.flatten_jd_skills()

        matched = sorted(resume.intersection(jd))

        missing = sorted(jd.difference(resume))

        return matched, missing
    
    def calculate_score(self, matched, jd_skills):

        if len(jd_skills) == 0:
            return 0

        score = (len(matched) / len(jd_skills)) * 100

        return round(score)