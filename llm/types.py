from abc import ABC, abstractmethod
from typing import Any, Optional


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
