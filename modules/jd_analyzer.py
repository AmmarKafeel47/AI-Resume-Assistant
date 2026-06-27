import json

from services.ai.provider_factory import ProviderFactory
from modules.prompt_loader import PromptLoader


class JDAnalyzer:

    def __init__(self):
        self.ai = ProviderFactory.get_provider()

    def analyze(self, job_description):

        prompt = PromptLoader.load(
            "prompts/analyze_jd.txt",
            {
                "JOB_DESCRIPTION": job_description
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