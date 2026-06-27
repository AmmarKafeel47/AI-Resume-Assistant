import json
import re

from services.ai.provider_factory import ProviderFactory
from modules.prompt_loader import PromptLoader
from modules.json_parser import JsonParser

class RecommendationEngine:

    def __init__(self):
        self.ai = ProviderFactory.get_provider()

    def generate(self, resume_json, jd_json, match_result):

        prompt = PromptLoader.load(
            "prompts/recommendation_prompt.txt",
            {
                "RESUME": resume_json,
                "JD": jd_json,
                "MATCH": match_result
            }
        )

        response = self.ai.generate(prompt)

        # Remove <think>...</think> if present
        response = re.sub(
            r"<think>.*?</think>",
            "",
            response,
            flags=re.DOTALL
        ).strip()

        # Extract only the JSON object
        match = re.search(r"\{.*\}", response, re.DOTALL)

        if match:
            response = match.group()

        try:
            return JsonParser.parse(response)

        except Exception:

            return {
                "error": "AI returned invalid JSON.",
                "raw_response": response
            }