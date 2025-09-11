from typing import Callable, ClassVar, Mapping

from .table_config_provider import TableConfigProvider

_RESPONSE_EXTRAS_PROVIDERS: set[type] = set()


class ResponseExtrasProvider(TableConfigProvider):
    """Models that expose response-only virtual fields."""

    __tigrbl_response_extras__: ClassVar[
        Mapping[str, Mapping[str, object]]
        | Callable[[], Mapping[str, Mapping[str, object]]]
    ] = {}

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        _RESPONSE_EXTRAS_PROVIDERS.add(cls)


def list_response_extras_providers():
    return sorted(_RESPONSE_EXTRAS_PROVIDERS, key=lambda c: c.__name__)
