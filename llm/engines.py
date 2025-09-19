import os

from anthropic import Anthropic
from dotenv import load_dotenv

from .types import LLMEngine

load_dotenv()


class AnthropicEngine(LLMEngine):
    def __init__(
        self,
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        temperature=0.7,
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
