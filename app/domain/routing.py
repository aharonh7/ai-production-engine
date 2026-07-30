from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProviderTarget:
    provider: str
    model: str


@dataclass(frozen=True, slots=True)
class SkillRoute:
    primary: ProviderTarget
    fallback: ProviderTarget | None = None
