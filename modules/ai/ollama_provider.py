import ollama
from pathlib import Path


class OllamaProvider:
    def __init__(self, model="qwen2.5:3b"):
        self.model = model

    def _load_prompt(self, prompt_name: str) -> str:
        prompt_path = Path("prompts") / prompt_name

        with open(prompt_path, "r", encoding="utf-8") as file:
            return file.read()

    def generate(self, prompt_name: str, **kwargs):

        prompt = self._load_prompt(prompt_name)

        for key, value in kwargs.items():
            prompt = prompt.replace(f"{{{{{key}}}}}", value)

        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response["message"]["content"]

        except Exception as e:
            raise RuntimeError(
                f"Failed to communicate with Ollama.\n\n{e}"
            )