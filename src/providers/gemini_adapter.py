import time
from src.core.interfaces import ProviderResponse
from src.providers.base import ProviderAdapter
try:
    import google.generativeai as genai
except:
    genai = None

class GeminiAdapter(ProviderAdapter):
    def __init__(self, api_key, default_model="gemini-1.5-pro"):
        if genai is None:
            raise ImportError("google-generativeai not installed")
        genai.configure(api_key=api_key)
        self.default_model = default_model
    def generate(self, prompt, system_prompt=None, temperature=0.7, max_tokens=4096, model=None, **kwargs):
        model = model or self.default_model
        start = time.time()
        try:
            model_obj = genai.GenerativeModel(model)
            response = model_obj.generate_content(prompt if not system_prompt else f"{system_prompt}\n\n{prompt}")
            return ProviderResponse(
                content=response.text,
                provider="google",
                model=model,
                cost=0.0
            )
        except Exception as e:
            raise Exception(f"Gemini error: {e}")
