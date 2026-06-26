from abc import ABC, abstractmethod


class BaseProvider(ABC):

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a response from the AI model."""
        pass