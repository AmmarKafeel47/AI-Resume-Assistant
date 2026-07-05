from modules.docx_exporter import DocxExporter

resume_json = {
    "personal_information": {
        "name": "Ammar Kafeel",
        "email": "ammarkafeel26627@gmail.com",
        "phone": "+92 3355524574",
        "linkedin": "linkedin.com/in/ammarkafeel",
        "github": "github.com/ammarkafeel"
    },
"summary": "MSc Data Science graduate with expertise in Python, Machine Learning and AI. Experienced in reinforcement learning, data analytics and predictive modelling.",

"headline": "Machine Learning Engineer",

"skills": {

    "programming_languages": [
        "Python",
        "SQL"
    ],

    "cloud": [
        "AWS",
        "Azure"
    ],

    "tools": [
        "Git",
        "Jupyter Notebook",
        "TensorFlow",
        "Plotly"
    ]
},
"experience": [
    {
        "job_title": "Supervisor Manager",
        "company": "Nando's UK & Ireland",
        "location": "London, UK",
        "start_date": "2023",
        "end_date": "2025",
        "responsibilities": [
            "Led recruitment, onboarding and training initiatives",
            "Utilized Looker dashboards to monitor KPIs",
            "Analyzed customer feedback using Yumpingo"
        ]
    },
    {
        "job_title": "Data Science Lab Assistant",
        "company": "University of Roehampton",
        "location": "London, UK",
        "start_date": "2023",
        "end_date": "2024",
        "responsibilities": [
            "Assisted in feature engineering and model evaluation",
            "Delivered Python and Machine Learning workshops"
        ]
    }
],
"projects": [
    {
        "title": "UAV Route Navigation Using Deep Reinforcement Learning",
        "description": "Developed route optimization models using PPO, DQN and DDQN algorithms.",
        "technologies": [
            "Python",
            "PPO",
            "DQN",
            "DDQN"
        ]
    },
    {
        "title": "Diabetic Retinopathy Detection",
        "description": "Built a CNN model and deployed it using Django.",
        "technologies": [
            "TensorFlow",
            "CNN",
            "Django"
        ]
    }
],
"education": [
    {
        "degree": "MSc Data Science",
        "institution": "University of Roehampton",
        "dates": "2023 - 2024",
        "description": "Distinction"
    },
    {
        "degree": "BSc Software Engineering",
        "institution": "SZABIST",
        "dates": "2018 - 2022",
        "description": "CGPA: 3.15"
    }
],
"certifications": [
    "Google Data Analytics Professional Certificate",
    "Microsoft Azure AI Fundamentals"
],
"languages": [
    {
        "language": "English",
        "proficiency": "Fluent"
    },
    {
        "language": "Urdu",
        "proficiency": "Native"
    }
],
}

exporter = DocxExporter(resume_json)

file = exporter.export()

print(file)