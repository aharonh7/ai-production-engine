class ProviderRegistry:
    def __init__(self):
        self._providers = {}
    def register(self, name, adapter):
        self._providers[name] = adapter
    def get(self, name):
        return self._providers.get(name)
    def list_providers(self):
        return list(self._providers.keys())
