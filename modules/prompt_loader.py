import json


class PromptLoader:

    @staticmethod
    def load(prompt_path, replacements):

        with open(prompt_path, "r", encoding="utf-8") as file:
            prompt = file.read()

        for key, value in replacements.items():

            if not isinstance(value, str):
                value = json.dumps(value, indent=2)

            prompt = prompt.replace(
                "{{" + key + "}}",
                value
            )

        return prompt