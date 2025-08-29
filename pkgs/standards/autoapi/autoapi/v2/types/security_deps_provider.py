from typing import Callable, ClassVar, Iterable

from .table_config_provider import TableConfigProvider

_SECURITY_DEPS_PROVIDERS: set[type] = set()


class SecurityDepsProvider(TableConfigProvider):
    """Models that define extra security dependencies for routes."""

    __autoapi_security_deps__: ClassVar[Iterable | Callable[[], Iterable]] = ()

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        _SECURITY_DEPS_PROVIDERS.add(cls)


def list_security_deps_providers():
    return sorted(_SECURITY_DEPS_PROVIDERS, key=lambda c: c.__name__)
