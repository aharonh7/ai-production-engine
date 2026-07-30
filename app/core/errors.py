class EngineError(Exception):
    """Base application error."""


class ProviderNotConfiguredError(EngineError):
    pass


class ProviderCallError(EngineError):
    pass


class RoutingConfigurationError(EngineError):
    pass
