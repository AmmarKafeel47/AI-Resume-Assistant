import json

from services.ai.provider_factory import ProviderFactory
from modules.prompt_loader import PromptLoader


class CoverLetterGenerator:

    def __init__(self):
        self.ai = ProviderFactory.get_provider()

    def generate(
        self,
        resume_json,
        tailored_resume,
        jd_json
    ):

        prompt = PromptLoader.load(
            "prompts/cover_letter.txt",
            {
                "RESUME": resume_json,
                "TAILORED_RESUME": tailored_resume,
                "JD": jd_json
            }
        )

        response = self.ai.generate(prompt)

        try:
            return json.loads(response)

        except json.JSONDecodeError:

            return {
                "error": "AI returned invalid JSON.",
                "raw_response": response
            }