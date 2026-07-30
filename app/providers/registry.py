from app.core.errors import ProviderNotConfiguredError
from app.domain.provider import AIProvider


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, AIProvider] = {}

    def register(self, provider: AIProvider) -> None:
        self._providers[provider.name] = provider

    def get(self, name: str) -> AIProvider:
        try:
            return self._providers[name]
        except KeyError as exc:
            raise ProviderNotConfiguredError(f"Unknown provider: {name}") from exc

    def names(self) -> list[str]:
        return sorted(self._providers)
