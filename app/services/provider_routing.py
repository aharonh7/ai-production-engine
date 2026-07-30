from pathlib import Path

import yaml

from app.core.errors import RoutingConfigurationError
from app.domain.routing import ProviderTarget, SkillRoute


class ProviderRoutingService:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self._config: dict = {}
        self.reload()

    def reload(self) -> None:
        try:
            with self.config_path.open("r", encoding="utf-8") as handle:
                self._config = yaml.safe_load(handle) or {}
        except Exception as exc:
            raise RoutingConfigurationError(f"Cannot load routing file: {exc}") from exc

    def route_for(self, skill_id: str) -> SkillRoute:
        default = self._config.get("default", {})
        skill = self._config.get("skills", {}).get(skill_id, {})
        provider = skill.get("provider") or default.get("provider")
        model = skill.get("model") or default.get("model")
        if not provider or not model:
            raise RoutingConfigurationError(f"No provider/model configured for skill '{skill_id}'")

        fallback_cfg = skill.get("fallback")
        fallback = None
        if fallback_cfg:
            fallback = ProviderTarget(
                provider=fallback_cfg["provider"],
                model=fallback_cfg["model"],
            )
        return SkillRoute(
            primary=ProviderTarget(provider=provider, model=model),
            fallback=fallback,
        )
