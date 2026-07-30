from time import perf_counter

from app.core.errors import ProviderCallError, ProviderNotConfiguredError
from app.domain.provider import GenerationRequest, GenerationResult


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, api_key: str | None):
        self.api_key = api_key

    def capabilities(self) -> set[str]:
        return {"text", "tool_use", "long_context"}

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        if not self.api_key:
            raise ProviderNotConfiguredError("ANTHROPIC_API_KEY is missing")
        try:
            from anthropic import AsyncAnthropic
            client = AsyncAnthropic(api_key=self.api_key)
            started = perf_counter()
            response = await client.messages.create(
                model=request.model or "claude-sonnet-4-5",
                max_tokens=request.max_tokens or 4096,
                temperature=request.temperature,
                system=request.system_prompt or "",
                messages=[{"role": "user", "content": request.prompt}],
            )
            content = "".join(block.text for block in response.content if hasattr(block, "text"))
            return GenerationResult(
                content=content,
                provider=self.name,
                model=request.model or "claude-sonnet-4-5",
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                latency_ms=int((perf_counter() - started) * 1000),
                finish_reason=response.stop_reason,
                raw_response=response.model_dump(),
            )
        except ProviderNotConfiguredError:
            raise
        except Exception as exc:
            raise ProviderCallError(f"Anthropic call failed: {exc}") from exc
