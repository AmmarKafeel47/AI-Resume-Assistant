import re


SKILL_GROUPS = {

    # Programming Languages
    "python": [
        "python"
    ],

    "sql": [
        "sql",
        "mysql",
        "postgresql",
        "sqlite",
        "mssql",
        "sql server",
        "relational database",
        "relational databases"
    ],

    "r": [
        "r",
        "r language",
        "r programming"
    ],

    # Machine Learning
    "machine learning": [
        "machine learning",
        "ml",
        "supervised learning",
        "unsupervised learning",
        "supervised & unsupervised learning",
        "regression",
        "linear regression",
        "ridge regression",
        "lasso regression",
        "classification",
        "clustering",
        "k-means",
        "hierarchical clustering",
        "predictive modelling",
        "predictive modeling",
        "predictive models",
        "model evaluation",
        "model training",
        "scikit-learn",
        "sklearn"
    ],

    "deep learning": [
        "deep learning",
        "cnn",
        "rnn",
        "lstm",
        "neural network",
        "artificial neural network",
        "tensorflow",
        "keras",
        "pytorch"
    ],

    "reinforcement learning": [
        "reinforcement learning",
        "ppo",
        "proximal policy optimization",
        "dqn",
        "deep q-network",
        "ddqn",
        "double deep q-network",
        "q-learning",
        "policy optimization"
    ],

    # Data Analysis
    "data analysis": [
        "data analysis",
        "data analytics",
        "eda",
        "exploratory data analysis",
        "pandas",
        "numpy",
        "data cleaning",
        "data wrangling",
        "data preprocessing",
        "statistical analysis",
        "statistics",
        "feature engineering",
        "mathematical techniques",
        "mathematical modelling",
        "mathematical modeling",
        "modelling frameworks",
        "modeling frameworks",
        "broad range of mathematical techniques",
        "analytical techniques",
        "statistical modelling",
        "statistical modeling",
        "comfortable processing large data sets",
        "comfortable processing large data sets for model estimation, insights and analysis",
        "processing large data sets",
        "large data sets",
        "model estimation",
        "insights and analysis",
    ],

    # Data Visualization
    "data visualization": [
        "data visualization",
        "visualization",
        "visualisation",
        "matplotlib",
        "seaborn",
        "plotly",
        "tableau",
        "power bi",
        "dashboard",
        "dashboards",
        "looker"
    ],

    # Cloud
    "cloud": [
        "cloud",
        "cloud computing",
        "cloud computing platform",
        "cloud platform",
        "cloud platforms",
        "aws",
        "azure",
        "gcp",
        "google cloud"
    ],

    # MLOps / Deployment
    "mlops": [
        "mlops",
        "model monitoring",
        "model deployment",
        "deployment",
        "scalability",
        "optimization",
        "optimisation"
    ],

    # Version Control
    "git": [
        "git",
        "github",
        "git/github",
        "version control"
    ],

    # Other Tools
    "excel": [
        "excel",
        "microsoft excel"
    ],

    "jupyter notebook": [
        "jupyter",
        "jupyter notebook"
    ],

    "web development": [
        "django"
    ],
    # Soft Skills
    "communication": [
        "communication",
        "communication skills",
        "strong communication skills",
        "clear communication",
        "stakeholder communication",
        "technical communication",
        "non-technical stakeholders",
        "technical and non-technical stakeholders",
        "explain models",
        "explain outcomes",
        "present findings",
        "collaboration",
        "collaborated"
    ],
    
    # Software Engineering
"software engineering": [
    "software engineering",
    "software engineering skills",
    "unit testing",
    "object-oriented programming",
    "oop",
    "production-quality code",
    "clean code",
    "clean, production-quality code",
    "best software engineering practices"
],

# LLMs
"llms": [
    "llm",
    "llms",
    "large language model",
    "large language models",
    "experience implementing llms in production",
    "implementing llms in production"
],

# Retail / Domain Analytics
"retail analytics": [
    "retail analytics",
    "retail",
    "consumer goods",
    "price optimisation",
    "price optimization",
    "demand forecasting",
    "inventory optimisation",
    "inventory optimization"
],
}


SKILL_CATEGORIES = {

    "Programming Languages": {
        "python",
        "sql",
        "r"
    },

    "Machine Learning": {
        "machine learning",
        "deep learning",
        "reinforcement learning"
    },

    "Data Analysis": {
        "data analysis",
        "excel",
        "jupyter notebook"
    },

    "Data Visualization": {
        "data visualization"
    },

    "Cloud": {
        "cloud"
    },

    "MLOps": {
        "mlops"
    },

    "Version Control": {
        "git"
    },

    "Web Development": {
        "web development"
    },
    "Soft Skills": {
        "communication"
    },
    "Software Engineering": {
    "software engineering"
    },

    "AI / LLMs": {
        "llms"
    },

    "Domain Knowledge": {
        "retail analytics"
    },
}


def clean_skill_text(skill):
    """
    Clean skill text before matching.
    """

    if not skill:
        return ""

    skill = str(skill).lower().strip()
    skill = re.sub(r"\s+", " ", skill)

    return skill


def canonical_skill(skill: str):
    """
    Convert similar skills into one canonical ATS skill.
    Example:
    TensorFlow -> deep learning
    Tableau -> data visualization
    PPO -> reinforcement learning
    """

    skill = clean_skill_text(skill)

    if not skill:
        return ""

    direct_aliases = {
        # Data analysis phrase cleanup
        "comfortable processing large data sets for model estimation, insights and analysis": "data analysis",
        "comfortable processing large data sets": "data analysis",
        "processing large data sets": "data analysis",
        "large data sets": "data analysis",
        "model estimation": "data analysis",
        "insights and analysis": "data analysis",

        # LLM cleanup
        "experience implementing llms in production": "llms",
        "implementing llms in production": "llms",
        "llm": "llms",
        "llms": "llms",
        "large language model": "llms",
        "large language models": "llms",

        # Software engineering cleanup
        "software engineering": "software engineering",
        "software engineering skills": "software engineering",
        "unit testing": "software engineering",
        "object-oriented programming": "software engineering",
        "oop": "software engineering",
        "production-quality code": "software engineering",
        "clean production-quality code": "software engineering",
        "best software engineering practices": "software engineering",

        # Domain cleanup
        "retail analytics": "retail analytics",
        "retail": "retail analytics",
        "consumer goods": "retail analytics",
        "price optimisation": "retail analytics",
        "price optimization": "retail analytics",
        "demand forecasting": "retail analytics",
        "inventory optimisation": "retail analytics",
        "inventory optimization": "retail analytics"
    }

    if skill in direct_aliases:
        return direct_aliases[skill]

    for phrase, canonical in direct_aliases.items():

        if len(phrase) > 3 and phrase in skill:
            return canonical
    
    for canonical, aliases in SKILL_GROUPS.items():

        canonical_clean = clean_skill_text(canonical)

        if skill == canonical_clean:
            return canonical

        for alias in aliases:

            alias_clean = clean_skill_text(alias)

            if skill == alias_clean:
                return canonical

            # Substring matching for phrases like:
            # "Version control with Git"
            # "Experience with data visualization tools"
            # Avoid matching very short aliases like "r"
            if len(alias_clean) > 2:

                pattern = r"\b" + re.escape(alias_clean) + r"\b"

                if re.search(pattern, skill):
                    return canonical

    return skill


def get_skill_category(skill: str):
    """
    Return the ATS category for a skill.
    """

    skill = canonical_skill(skill)

    direct_categories = {
        "software engineering": "Software Engineering",
        "llms": "AI / LLMs",
        "retail analytics": "Domain Knowledge",
        "commercial awareness": "Soft Skills"
    }

    if skill in direct_categories:
        return direct_categories[skill]

    for category, skills in SKILL_CATEGORIES.items():

        if skill in skills:
            return category

    return "Other"