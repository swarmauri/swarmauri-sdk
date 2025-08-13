from typing import Any, Callable, ClassVar, Mapping, MutableMapping

from .table_config_provider import TableConfigProvider

_RESPONSE_EXTRA_PROVIDERS: set[type] = set()


class ResponseExtrasProvider(TableConfigProvider):
    """Models that expose additional fields in API responses."""

    __autoapi_response_extras__: ClassVar[
        Mapping[str, Callable[[MutableMapping[str, Any], Any], Mapping[str, Any]]]
    ] = {}

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        _RESPONSE_EXTRA_PROVIDERS.add(cls)


def list_response_extra_providers():
    return sorted(_RESPONSE_EXTRA_PROVIDERS, key=lambda c: c.__name__)
