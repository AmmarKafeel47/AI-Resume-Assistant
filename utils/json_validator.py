import json
import re


class JSONValidator:

    @staticmethod
    def validate(response):
        """
        Validate and parse AI JSON response.
        Handles common local LLM issues:
        - markdown code fences
        - text before/after JSON
        - extra whitespace
        """

        if isinstance(response, dict):
            return True, response

        if not response:
            return False, {
                "error": "AI returned empty response.",
                "raw_response": response
            }

        text = str(response).strip()

        # Remove markdown fences if present
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

        # First direct parse
        try:
            return True, json.loads(text)

        except json.JSONDecodeError:
            pass

        # Try extracting JSON object from response
        extracted = JSONValidator.extract_json_object(text)

        if extracted:
            try:
                return True, json.loads(extracted)

            except json.JSONDecodeError:
                pass

        return False, {
            "error": "AI returned invalid JSON.",
            "raw_response": response
        }

    @staticmethod
    def extract_json_object(text):
        """
        Extract the first complete JSON object from text using brace matching.
        """

        start = text.find("{")

        if start == -1:
            return None

        brace_count = 0
        in_string = False
        escape = False

        for index in range(start, len(text)):

            char = text[index]

            if escape:
                escape = False
                continue

            if char == "\\":
                escape = True
                continue

            if char == '"':
                in_string = not in_string
                continue

            if not in_string:

                if char == "{":
                    brace_count += 1

                elif char == "}":
                    brace_count -= 1

                    if brace_count == 0:
                        return text[start:index + 1]

        return None