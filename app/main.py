from fastapi import FastAPI

from app.api.routes import router
from app.core.settings import settings
from app.db import models  # noqa: F401
from app.db.session import init_db
from app.providers.anthropic_provider import AnthropicProvider
from app.providers.deepseek_provider import DeepSeekProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.openai_provider import OpenAIProvider
from app.providers.registry import ProviderRegistry
from app.services.generation_service import GenerationService
from app.services.provider_routing import ProviderRoutingService

provider_registry = ProviderRegistry()
provider_registry.register(OpenAIProvider(settings.openai_api_key))
provider_registry.register(AnthropicProvider(settings.anthropic_api_key))
provider_registry.register(GeminiProvider(settings.gemini_api_key))
provider_registry.register(DeepSeekProvider(settings.deepseek_api_key))

routing_service = ProviderRoutingService(settings.provider_routing_file)
generation_service = GenerationService(provider_registry, routing_service)

app = FastAPI(title="AI Production Engine", version="0.1.0")
app.include_router(router, prefix="/api")


@app.on_event("startup")
def startup() -> None:
    settings.storage_root.mkdir(parents=True, exist_ok=True)
    init_db()
