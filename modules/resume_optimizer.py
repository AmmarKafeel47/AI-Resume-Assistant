import copy


class ResumeOptimizer:


    # =====================================================
    # Optimization Settings
    # =====================================================

    MAX_SUMMARY_WORDS = 60

    MAX_EXPERIENCE_BULLETS = 3

    MAX_PROJECTS = 3

    MAX_CERTIFICATIONS = 3

    MAX_EDUCATION_ENTRIES = 2

    MAX_LANGUAGE_ENTRIES = 3

    MIN_FONT_SIZE = 10
    
    TARGET_LAYOUT_SCORE = 100
    
    def __init__(self, resume):

        # Work on a copy so the original resume stays unchanged
        self.resume = copy.deepcopy(resume)

    def optimize(self):

        # First estimate current resume size
        layout_score = self.estimate_layout_score()

        # If already compact enough,
        # don't modify anything.
        if layout_score <= self.TARGET_LAYOUT_SCORE:

            self.resume["layout_score"] = layout_score

            self.resume["optimization_level"] = "None"

            return self.resume

        # -------------------------------------------------
        # Stage 1
        # Light Optimization
        # -------------------------------------------------

        self.optimize_summary()

        self.optimize_projects()

        layout_score = self.estimate_layout_score()

        if layout_score <= self.TARGET_LAYOUT_SCORE:

            self.resume["layout_score"] = layout_score

            self.resume["optimization_level"] = "Light"

            return self.resume

        # -------------------------------------------------
        # Stage 2
        # Medium Optimization
        # -------------------------------------------------

        self.optimize_experience()

        self.optimize_certifications()

        layout_score = self.estimate_layout_score()

        if layout_score <= self.TARGET_LAYOUT_SCORE:

            self.resume["layout_score"] = layout_score

            self.resume["optimization_level"] = "Medium"

            return self.resume

        # -------------------------------------------------
        # Stage 3
        # Heavy Optimization
        # -------------------------------------------------

        self.optimize_education()

        self.optimize_languages()

        layout_score = self.estimate_layout_score()

        self.resume["layout_score"] = layout_score

        self.resume["optimization_level"] = "Heavy"

        return self.resume

    # ----------------------------------------------------
    # Summary
    # ----------------------------------------------------

    def optimize_summary(self):

        summary = self.resume.get("summary", "").strip()

        if not summary:
            return

        words = summary.split()

        # Already short enough
        if len(words) <= self.MAX_SUMMARY_WORDS:
            return

        # ---------------------------------------------
        # Split into sentences
        # ---------------------------------------------

        sentences = summary.split(". ")

        optimized = ""

        word_count = 0

        for sentence in sentences:

            sentence = sentence.strip()

            if not sentence:
                continue

            sentence_words = len(sentence.split())

            if word_count + sentence_words > self.MAX_SUMMARY_WORDS:
                break

            if optimized:
                optimized += ". "

            optimized += sentence

            word_count += sentence_words

        # Make sure the summary ends with a full stop
        optimized = optimized.strip()

        if optimized and not optimized.endswith("."):
            optimized += "."

        self.resume["summary"] = optimized
        
    # ----------------------------------------------------
    # Experience
    # ----------------------------------------------------
 
    def optimize_experience(self):

        experience = self.resume.get("experience", [])

        if not experience:
            return

        # Keywords that typically indicate stronger impact
        impact_keywords = [
            "led",
            "managed",
            "developed",
            "built",
            "created",
            "improved",
            "increased",
            "reduced",
            "optimized",
            "implemented",
            "designed",
            "analyzed",
            "trained",
            "delivered",
            "deployed",
            "automated"
        ]

        for job in experience:

            responsibilities = job.get("responsibilities", [])

            if not responsibilities:
                continue

            scored_responsibilities = []

            for responsibility in responsibilities:

                score = 0

                text = responsibility.lower()

                # Reward impactful action verbs
                for keyword in impact_keywords:

                    if keyword in text:
                        score += 10

                # Reward longer, more detailed bullets
                score += len(text.split())

                scored_responsibilities.append(
                    (score, responsibility)
                )

            # Highest scoring first
            scored_responsibilities.sort(
                reverse=True,
                key=lambda x: x[0]
            )

            # Keep top bullets only
            top_bullets = [
                bullet
                for _, bullet in scored_responsibilities[
                    : self.MAX_EXPERIENCE_BULLETS
                ]
            ]

            job["responsibilities"] = top_bullets
        
        
    # ----------------------------------------------------
    # Projects
    # ----------------------------------------------------

    def optimize_projects(self):

        projects = self.resume.get("projects", [])

        if not projects:
            return

        scored_projects = []

        impact_keywords = [
            "machine learning",
            "deep learning",
            "artificial intelligence",
            "reinforcement learning",
            "nlp",
            "computer vision",
            "tensorflow",
            "pytorch",
            "django",
            "flask",
            "tableau",
            "power bi",
            "sql",
            "python",
            "aws",
            "azure",
            "deployment",
            "api"
        ]

        for project in projects:

            score = 0

            title = project.get("title", "").lower()
            description = project.get("description", "").lower()
            technologies = project.get("technologies", [])

            text = title + " " + description

            # -----------------------------------------
            # Valuable technologies
            # -----------------------------------------

            score += len(technologies) * 2

            # -----------------------------------------
            # Impact keywords
            # -----------------------------------------

            for keyword in impact_keywords:

                if keyword in text:
                    score += 5

            # -----------------------------------------
            # Description length
            # -----------------------------------------

            score += len(description.split())

            scored_projects.append((score, project))

        # Highest score first
        scored_projects.sort(
            reverse=True,
            key=lambda x: x[0]
        )

        # Keep best projects only
        self.resume["projects"] = [
            project
            for _, project in scored_projects[:self.MAX_PROJECTS]
        ]

    # ----------------------------------------------------
    # Education
    # ----------------------------------------------------

    def optimize_education(self):

        pass

    # ----------------------------------------------------
    # Certifications
    # ----------------------------------------------------

    def optimize_certifications(self):

        pass

    # ----------------------------------------------------
    # Languages
    # ----------------------------------------------------

    def optimize_languages(self):

        pass
    
    # ----------------------------------------------------
    # Estimate Resume Size
    # ----------------------------------------------------

    def estimate_layout_score(self):

        score = 0

        # ------------------------------------------
        # Summary
        # ------------------------------------------

        summary = self.resume.get("summary", "")

        score += len(summary.split()) * 0.4

        # ------------------------------------------
        # Skills
        # ------------------------------------------

        skills = self.resume.get("skills", {})

        for category in skills.values():

            score += len(category)

        # ------------------------------------------
        # Experience
        # ------------------------------------------

        for job in self.resume.get("experience", []):

            score += 4

            responsibilities = job.get(
                "responsibilities",
                []
            )

            score += len(responsibilities) * 2

        # ------------------------------------------
        # Projects
        # ------------------------------------------

        for project in self.resume.get("projects", []):

            score += 5

        # ------------------------------------------
        # Education
        # ------------------------------------------

        score += len(
            self.resume.get("education", [])
        ) * 4

        # ------------------------------------------
        # Certifications
        # ------------------------------------------

        score += len(
            self.resume.get("certifications", [])
        )

        # ------------------------------------------
        # Languages
        # ------------------------------------------

        score += len(
            self.resume.get("languages", [])
        )

        return round(score)
    