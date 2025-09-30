import os
from abc import ABC, abstractmethod
from typing import Any, Optional

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class LLMEngine(ABC):
    """Abstract base class for LLM engines."""

    def __init__(
        self,
        model: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        system: Optional[str] = None,
    ):
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.system = system

    @abstractmethod
    def send_message(self, content: str) -> Any:
        """Send a message to the LLM and return the response."""
        pass


class AnthropicEngine(LLMEngine):
    def __init__(
        self,
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        temperature=0.1,
        system=None,
    ):
        super().__init__(model, max_tokens, temperature, system)
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def send_message(self, content: str):
        kwargs = {
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": content}],
            "model": self.model,
            "temperature": self.temperature,
        }
        if self.system:
            kwargs["system"] = self.system

        message = self.client.messages.create(**kwargs)
        return message.content
