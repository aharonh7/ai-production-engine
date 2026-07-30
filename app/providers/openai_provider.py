from time import perf_counter

from app.core.errors import ProviderCallError, ProviderNotConfiguredError
from app.domain.provider import GenerationRequest, GenerationResult


class OpenAIProvider:
    name = "openai"

    def __init__(self, api_key: str | None):
        self.api_key = api_key

    def capabilities(self) -> set[str]:
        return {"text", "structured_output", "tool_use", "long_context"}

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        if not self.api_key:
            raise ProviderNotConfiguredError("OPENAI_API_KEY is missing")
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key)
            started = perf_counter()
            response = await client.responses.create(
                model=request.model or "gpt-5-mini",
                instructions=request.system_prompt,
                input=request.prompt,
                max_output_tokens=request.max_tokens,
            )
            usage = getattr(response, "usage", None)
            return GenerationResult(
                content=response.output_text,
                provider=self.name,
                model=request.model or "gpt-5-mini",
                input_tokens=getattr(usage, "input_tokens", None),
                output_tokens=getattr(usage, "output_tokens", None),
                latency_ms=int((perf_counter() - started) * 1000),
                raw_response=response.model_dump(),
            )
        except ProviderNotConfiguredError:
            raise
        except Exception as exc:
            raise ProviderCallError(f"OpenAI call failed: {exc}") from exc
