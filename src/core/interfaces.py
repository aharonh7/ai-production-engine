from abc import ABC, abstractmethod
from typing import Optional

class ProviderResponse:
    def __init__(self, content, provider=None, model=None, prompt_tokens=0, completion_tokens=0, total_tokens=0, cost=0.0, finish_reason=None):
        self.content = content
        self.provider = provider
        self.model = model
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens
        self.cost = cost
        self.finish_reason = finish_reason  # "stop" = תקין, "length" = נחתך עקב max_tokens

    @property
    def was_truncated(self) -> bool:
        return self.finish_reason == "length"

class ProviderAdapter(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> ProviderResponse:
        pass
