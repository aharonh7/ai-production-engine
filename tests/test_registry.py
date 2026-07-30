import pytest

from app.core.errors import ProviderNotConfiguredError
from app.providers.registry import ProviderRegistry


class FakeProvider:
    name = "fake"

    async def generate(self, request):
        return None

    def capabilities(self):
        return {"text"}


def test_registry_registers_provider() -> None:
    registry = ProviderRegistry()
    registry.register(FakeProvider())
    assert registry.get("fake").name == "fake"


def test_registry_rejects_unknown_provider() -> None:
    registry = ProviderRegistry()
    with pytest.raises(ProviderNotConfiguredError):
        registry.get("missing")
