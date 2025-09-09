from abc import abstractmethod

from .table_config_provider import TableConfigProvider

_NESTED_PATH_PROVIDERS: set[type] = set()


class NestedPathProvider(TableConfigProvider):
    """Models that supply nested route prefixes."""

    @classmethod
    @abstractmethod
    def __tigrbl_nested_paths__(cls) -> str | None:
        """Return hierarchical path prefix for nested routes."""

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        _NESTED_PATH_PROVIDERS.add(cls)


def list_nested_path_providers():
    return sorted(_NESTED_PATH_PROVIDERS, key=lambda c: c.__name__)
