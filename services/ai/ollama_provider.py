import ollama


class OllamaProvider:

    def __init__(self, model="qwen2.5:3b"):
        self.model = model

    def generate(self, prompt: str):

        try:

            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                format="json"
            )

            return response["message"]["content"]

        except Exception as e:

            raise RuntimeError(
                f"Failed to communicate with Ollama.\n\n{e}"
            )