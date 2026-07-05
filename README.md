# ResumePilot AI

ResumePilot AI is an AI-powered resume tailoring and ATS analysis assistant built with Streamlit. It helps users upload a resume, analyze a job description, calculate an ATS-style match score, identify skill gaps, generate career recommendations, create a tailored resume, and export application documents.

---

## 🚀 Features
---

### 📄 Resume Analysis
- Upload resume in PDF or DOCX format
- Extract resume text
- Parse structured resume information
- Identify:
  - Candidate information
  - Skills
  - Experience
  - Projects
  - Education
  - Certifications
  - Languages

### 📋 Job Description Analysis
- Paste any job description
- Extract key hiring requirements
- Detect:
  - Job title
  - Company
  - Required skills
  - Preferred skills
  - Responsibilities
  - Tools and technologies
  - Cloud, database, and programming language requirements

### 🎯 ATS Match Dashboard
- Calculates a weighted ATS match score
- Separates required and preferred skills
- Shows:
  - Overall ATS score
  - Required skills score
  - Preferred skills score
  - Matched skills
  - Missing skills
  - Category-level performance

### 🤖 AI Career Coach
- Generates an executive summary
- Highlights candidate strengths
- Identifies priority skill gaps
- Suggests resume improvements
- Provides ATS keywords
- Recommends learning actions

### 📦 Application Package
- Generates a tailored resume
- Generates a cover letter
- Exports documents as DOCX
- Saves structured analysis output locally

### 🛠 Developer Tools
- View extracted resume text
- View structured resume JSON
- View job description JSON
- View match result JSON
- View recommendation JSON
- View tailored resume JSON

---

## 🧠 How It Works
---

ResumePilot AI follows this workflow:

```text
Upload Resume
        ↓
Extract Resume Text
        ↓
Analyze Resume with AI
        ↓
Paste Job Description
        ↓
Analyze Job Description
        ↓
Match Resume Against JD
        ↓
Generate Career Recommendations
        ↓
Generate Tailored Resume
        ↓
Generate Cover Letter
        ↓
Download Application Package

```


---

## 🏗️ Project Structure
---

```text
AI-Resume-Assistant/
│
├── app.py
│
├── modules/
│   ├── parser.py
│   ├── resume_analyzer.py
│   ├── jd_analyzer.py
│   ├── matcher.py
│   ├── recommendation_engine.py
│   ├── resume_generator.py
│   ├── cover_letter_generator.py
│   ├── docx_exporter.py
│   ├── cover_letter_exporter.py
│   ├── exporter.py
│   ├── normalizer.py
│   └── skill_dictionary.py
│
├── prompts/
│   ├── analyze_resume.txt
│   ├── analyze_jd.txt
│   ├── recommendation_prompt.txt
│   ├── tailored_resume.txt
│   └── cover_letter_prompt.txt
│
├── services/
│   └── ai/
│       ├── provider_factory.py
│       └── providers/
│
├── utils/
│   └── json_validator.py
│
├── outputs/
│
├── requirements.txt
└── README.md
```
---
## ⚙️ Tech Stack
---
- Python
- Streamlit
- Ollama
- Qwen 2.5
- PDFPlumber
- python-docx
- JSON-based AI parsing
- DOCX export
---
## 🧩 Core Modules
 ---
### parser.py

Extracts text from uploaded PDF and DOCX resumes.

### resume_analyzer.py

Uses AI to convert raw resume text into structured JSON.

### jd_analyzer.py

Analyzes job descriptions and extracts required/preferred skills, responsibilities, tools, and job metadata.

### matcher.py

Compares resume skills against job description requirements using weighted ATS-style scoring.

### skill_dictionary.py

Normalizes skill names and groups similar terms into canonical ATS skills.

#### Example:

```text
scikit-learn → machine learning
PPO / DQN / DDQN → reinforcement learning
Tableau / Power BI → data visualization
GCP / AWS / Azure → cloud
```

### recommendation_engine.py

Generates career recommendations based on the resume, job description, and ATS match result.

### resume_generator.py

Generates a tailored resume while preserving factual accuracy from the original resume.

### cover_letter_generator.py

Generates a role-specific cover letter.

### docx_exporter.py

Exports the tailored resume as a DOCX file.

### cover_letter_exporter.py

Exports the generated cover letter as a DOCX file.

---

## 📊 ATS Scoring
---
ResumePilot AI uses a weighted scoring system instead of simple keyword counting.

#### Example scoring logic:
```text
Required Skills = Higher Weight
Preferred Skills = Lower Weight
Matched Required Skills = Positive Score
Missing Required Skills = Higher Penalty
Missing Preferred Skills = Lower Penalty
```

The dashboard shows:

- Overall ATS Score
- Required Skills Score
- Preferred Skills Score
- Category Breakdown
- Matched Skills
- Missing Skills
---
## 🧪 Example Output
---
#### ATS Match Result
```text
Overall ATS Score: 62%
Required Skills Score: 62%
Preferred Skills Score: 52%
```

#### Matched Skills
```text
Python
Machine Learning
Data Analysis
Communication
Git
SQL
``` 
 
#### Missing Skills
```text
Cloud
MLOps
Software Engineering
LLMs
Retail Analytics
```
---
## 🖥️ Installation
---

### 1. Clone the repository
```text
git clone https://github.com/AmmarKafeel47/AI-Resume-Assistant.git

cd AI-Resume-Assistant 
```

### 2. Create a virtual environment
```text
python -m venv venv
```

### 3. Activate the virtual environment

For Windows PowerShell:
```text
venv\Scripts\activate
```
For macOS/Linux:
```text
source venv/bin/activate
```
### 4. Install dependencies
```text
pip install -r requirements.txt
```
---
## 🤖 Ollama Setup
---
This project is designed to work with a local Ollama model.

### 1. Install Ollama

Download and install Ollama from:
```text
https://ollama.com
```
### 2. Pull the model
```text
ollama pull qwen2.5:3b
```
### 3. Start Ollama
```text
ollama serve
```
---
## ▶️ Running the App
---
Run the Streamlit application:
```text
streamlit run app.py
```
Then open the local URL shown in the terminal:
```text
http://localhost:8501
```
---
## 📁 Outputs
---
Generated analysis and documents are saved locally inside the outputs/ folder.

Typical outputs include:
```text
outputs/
├── analysis_YYYYMMDD_HHMMSS/
│   ├── resume.json
│   ├── job_description.json
│   └── match_result.json
```
Generated DOCX files are available through the app download buttons.

---
## ✅ Recommended .gitignore
---
Add this to your ```.gitignore: ```
```
# Python
__pycache__/
*.pyc
*.pyo
*.pyd

# Virtual environment
venv/
.env

# Streamlit
.streamlit/secrets.toml

# Outputs
outputs/
*.docx

# OS files
.DS_Store
Thumbs.db
```

---
## 🔒 Notes on Accuracy
---

ResumePilot AI is designed to avoid adding unsupported information to the tailored resume. The system preserves factual sections from the original resume and uses AI mainly for analysis, recommendations, and rewriting support.

Users should always review generated resumes and cover letters before submitting job applications.

---
## 📌 Current Status
---
The project currently includes:

- Resume upload and parsing
- Resume analysis
- Job description analysis
- Weighted ATS matching
- Career coach recommendations
- Tailored resume generation
- Cover letter generation
- DOCX export
- Product-style Streamlit UI
- Developer tools for debugging

---
## 🚧 Future Improvements
---
Possible future enhancements:

- Login/authentication
- Multiple resume templates
- PDF export
- Job application tracker
- Resume version history
- LinkedIn profile optimization
- Skill learning roadmap
- Cloud deployment
- Database storage
- Multi-model provider support

---
## 👤 Author
---
Ammar Kafeel

Machine Learning Engineer / Data Science Practitioner

---
## 📄 License
---
This project is for educational and portfolio purposes. Add your preferred license before public distribution.