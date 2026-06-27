#------------Improve the fallback Parser----------------

import json
import re


class JsonParser:

    @staticmethod
    def parse(response):

        if isinstance(response, dict):
            return response

        response = response.strip()

        # Remove <think> tags
        response = re.sub(
            r"<think>.*?</think>",
            "",
            response,
            flags=re.DOTALL
        )

        # Extract JSON object
        match = re.search(
            r"\{.*\}",
            response,
            re.DOTALL
        )

        if match:
            response = match.group()

        return json.loads(response)
    
#every AI module can reuse this parser instead of duplicating parsing logic.