from typing import Callable, ClassVar, Mapping

from .table_config_provider import TableConfigProvider

_REQUEST_EXTRAS_PROVIDERS: set[type] = set()


class RequestExtrasProvider(TableConfigProvider):
    """Models that expose request-only virtual fields."""

    __tigrbl_request_extras__: ClassVar[
        Mapping[str, Mapping[str, object]]
        | Callable[[], Mapping[str, Mapping[str, object]]]
    ] = {}

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        _REQUEST_EXTRAS_PROVIDERS.add(cls)


def list_request_extras_providers():
    return sorted(_REQUEST_EXTRAS_PROVIDERS, key=lambda c: c.__name__)
