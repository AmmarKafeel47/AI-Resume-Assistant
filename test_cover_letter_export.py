from modules.cover_letter_exporter import CoverLetterExporter

cover = {
    "cover_letter":
"""Dear Hiring Manager,

I am writing to express my interest...

My experience includes Python, SQL and Machine Learning.

Sincerely,

Ammar Kafeel"""
}

resume = {
    "personal_information": {
        "name": "Ammar Kafeel"
    }
}

exporter = CoverLetterExporter(
    cover,
    resume
)

file = exporter.export()

print(file)