from abc import abstractmethod

from .table_config_provider import TableConfigProvider

_ALLOW_ANON_PROVIDERS: set[type] = set()


class AllowAnonProvider(TableConfigProvider):
    """Models that expose operations without authentication."""

    @classmethod
    @abstractmethod
    def __autoapi_allow_anon__(cls) -> set[str]:
        """Return a set of CRUD verb names that allow anonymous access."""

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        _ALLOW_ANON_PROVIDERS.add(cls)


def list_allow_anon_providers():
    return sorted(_ALLOW_ANON_PROVIDERS, key=lambda c: c.__name__)
