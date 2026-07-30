import time
from src.core.interfaces import ProviderResponse
from src.providers.base import ProviderAdapter
try:
    import openai
except:
    openai = None

class OpenAIAdapter(ProviderAdapter):
    def __init__(self, api_key, default_model="gpt-4o-mini"):
        if openai is None:
            raise ImportError("openai not installed")
        self.client = openai.OpenAI(api_key=api_key)
        self.default_model = default_model
    def generate(self, prompt, system_prompt=None, temperature=0.7, max_tokens=4096, model=None, **kwargs):
        model = model or self.default_model
        start = time.time()
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        try:
            response = self.client.chat.completions.create(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
            return ProviderResponse(
                content=response.choices[0].message.content,
                provider="openai",
                model=model,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
                cost=0.0
            )
        except Exception as e:
            raise Exception(f"OpenAI error: {e}")
