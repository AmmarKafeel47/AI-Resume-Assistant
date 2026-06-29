from modules.cover_letter_generator import CoverLetterGenerator

resume = {
    "summary": "Machine Learning Engineer with Python and AI experience."
}

tailored_resume = {
    "summary": "Tailored summary."
}

jd = {
    "job_title": "Data Scientist"
}

generator = CoverLetterGenerator()

result = generator.generate(
    resume,
    tailored_resume,
    jd
)

print(result)