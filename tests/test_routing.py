from pathlib import Path

from app.services.provider_routing import ProviderRoutingService


def test_write_chapter_route() -> None:
    service = ProviderRoutingService(Path("config/provider_routing.yaml"))
    route = service.route_for("write_chapter")
    assert route.primary.provider == "anthropic"
    assert route.fallback is not None
    assert route.fallback.provider == "openai"


def test_unknown_skill_uses_default() -> None:
    service = ProviderRoutingService(Path("config/provider_routing.yaml"))
    route = service.route_for("unknown_skill")
    assert route.primary.provider == "deepseek"
