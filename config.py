from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
PROMPT_DIR = BASE_DIR / "prompts"

OLLAMA_MODEL = "qwen2.5:3b"