from app.core.errors import ProviderCallError
from app.domain.provider import GenerationRequest, GenerationResult
from app.providers.registry import ProviderRegistry
from app.services.provider_routing import ProviderRoutingService


class GenerationService:
    def __init__(self, registry: ProviderRegistry, routing: ProviderRoutingService):
        self.registry = registry
        self.routing = routing

    async def run_skill(self, skill_id: str, request: GenerationRequest) -> GenerationResult:
        route = self.routing.route_for(skill_id)
        request.model = route.primary.model
        try:
            return await self.registry.get(route.primary.provider).generate(request)
        except Exception as primary_error:
            if route.fallback is None:
                raise
            fallback_request = GenerationRequest(
                prompt=request.prompt,
                system_prompt=request.system_prompt,
                model=route.fallback.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                response_schema=request.response_schema,
                metadata={**request.metadata, "fallback_from": route.primary.provider},
            )
            try:
                return await self.registry.get(route.fallback.provider).generate(fallback_request)
            except Exception as fallback_error:
                raise ProviderCallError(
                    f"Primary and fallback failed for skill '{skill_id}': "
                    f"{primary_error}; {fallback_error}"
                ) from fallback_error
