from time import perf_counter

import httpx

from app.core.errors import ProviderCallError, ProviderNotConfiguredError
from app.domain.provider import GenerationRequest, GenerationResult


class DeepSeekProvider:
    name = "deepseek"

    def __init__(self, api_key: str | None):
        self.api_key = api_key

    def capabilities(self) -> set[str]:
        return {"text", "structured_output", "long_context"}

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        if not self.api_key:
            raise ProviderNotConfiguredError("DEEPSEEK_API_KEY is missing")
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})
        payload = {
            "model": request.model or "deepseek-chat",
            "messages": messages,
            "temperature": request.temperature,
        }
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens
        try:
            started = perf_counter()
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(
                    "https://api.deepseek.com/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
            usage = data.get("usage", {})
            choice = data["choices"][0]
            return GenerationResult(
                content=choice["message"]["content"],
                provider=self.name,
                model=request.model or "deepseek-chat",
                input_tokens=usage.get("prompt_tokens"),
                output_tokens=usage.get("completion_tokens"),
                latency_ms=int((perf_counter() - started) * 1000),
                finish_reason=choice.get("finish_reason"),
                raw_response=data,
            )
        except ProviderNotConfiguredError:
            raise
        except Exception as exc:
            raise ProviderCallError(f"DeepSeek call failed: {exc}") from exc
