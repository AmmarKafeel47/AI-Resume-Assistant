import json
from modules.ai.ollama_provider import OllamaProvider


class JDAnalyzer:

    def __init__(self):
        self.ai = OllamaProvider()

    def analyze(self, job_description: str):

        result = self.ai.generate(
            "analyze_jd.txt",
            JOB_DESCRIPTION=job_description
        )

        return json.loads(result)