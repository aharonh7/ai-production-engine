import time
from src.core.interfaces import ProviderResponse
from src.providers.base import ProviderAdapter
try:
    import anthropic
except:
    anthropic = None

class AnthropicAdapter(ProviderAdapter):
    def __init__(self, api_key, default_model="claude-3-5-sonnet-20241022"):
        if anthropic is None:
            raise ImportError("anthropic not installed")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.default_model = default_model
    def generate(self, prompt, system_prompt=None, temperature=0.7, max_tokens=4096, model=None, **kwargs):
        model = model or self.default_model
        start = time.time()
        try:
            response = self.client.messages.create(
                model=model,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return ProviderResponse(
                content=response.content[0].text,
                provider="anthropic",
                model=model,
                cost=0.0
            )
        except Exception as e:
            raise Exception(f"Anthropic error: {e}")
