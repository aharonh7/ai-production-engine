from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(slots=True)
class GenerationRequest:
    prompt: str
    system_prompt: str | None = None
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int | None = None
    response_schema: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class GenerationResult:
    content: str
    provider: str
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    estimated_cost: float | None = None
    latency_ms: int | None = None
    finish_reason: str | None = None
    structured_data: dict[str, Any] | None = None
    raw_response: dict[str, Any] | None = None
    validation_status: str = "unvalidated"


class AIProvider(Protocol):
    name: str

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        ...

    def capabilities(self) -> set[str]:
        ...
