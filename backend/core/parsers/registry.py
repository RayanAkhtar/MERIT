from typing import Dict, Type
from core.parsers.base import BaseDataSource
from core.parsers.github import GitHubDataSource
from core.parsers.linkedin import LinkedInDataSource

# registry for data sources
# should allow easy addition of new data sources without significant
# changes to the rest of the codebase

class DataSourceRegistry:
    def __init__(self):
        self._sources: Dict[str, BaseDataSource] = {}
        self._register_defaults()

    def _register_defaults(self):
        self.register(GitHubDataSource())
        self.register(LinkedInDataSource())

    def register(self, source: BaseDataSource):
        self._sources[source.name] = source

    def get_source(self, name: str) -> BaseDataSource:
        source = self._sources.get(name)
        if not source:
            raise ValueError(f"Data source '{name}' is not registered.")
        return source

    def get_all_sources(self) -> Dict[str, BaseDataSource]:
        return self._sources

datasource_registry = DataSourceRegistry()
