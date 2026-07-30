from time import perf_counter

from app.core.errors import ProviderCallError, ProviderNotConfiguredError
from app.domain.provider import GenerationRequest, GenerationResult


class GeminiProvider:
    name = "gemini"

    def __init__(self, api_key: str | None):
        self.api_key = api_key

    def capabilities(self) -> set[str]:
        return {"text", "structured_output", "image_input", "long_context"}

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        if not self.api_key:
            raise ProviderNotConfiguredError("GEMINI_API_KEY is missing")
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model_name = request.model or "gemini-2.5-flash"
            model = genai.GenerativeModel(model_name, system_instruction=request.system_prompt)
            started = perf_counter()
            response = await model.generate_content_async(
                request.prompt,
                generation_config={
                    "temperature": request.temperature,
                    "max_output_tokens": request.max_tokens,
                },
            )
            usage = getattr(response, "usage_metadata", None)
            return GenerationResult(
                content=response.text,
                provider=self.name,
                model=model_name,
                input_tokens=getattr(usage, "prompt_token_count", None),
                output_tokens=getattr(usage, "candidates_token_count", None),
                latency_ms=int((perf_counter() - started) * 1000),
                raw_response={"text": response.text},
            )
        except ProviderNotConfiguredError:
            raise
        except Exception as exc:
            raise ProviderCallError(f"Gemini call failed: {exc}") from exc
