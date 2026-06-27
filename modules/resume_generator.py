import json

from services.ai.provider_factory import ProviderFactory
from modules.prompt_loader import PromptLoader


class ResumeGenerator:

    def __init__(self):
        self.ai = ProviderFactory.get_provider()

    def generate(
        self,
        resume_json,
        jd_json,
        match_result,
        recommendations
    ):

        prompt = PromptLoader.load(
            "prompts/tailored_resume.txt",
            {
                "RESUME": resume_json,
                "JD": jd_json,
                "MATCH": match_result,
                "RECOMMENDATIONS": recommendations
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