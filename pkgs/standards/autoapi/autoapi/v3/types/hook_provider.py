# autoapi/v3/types/hook_provider.py  – tiny helper module
from typing import TYPE_CHECKING, Callable

from .table_config_provider import TableConfigProvider

if TYPE_CHECKING:  # forward ref avoids circular import
    from autoapi.v3 import AutoAPI

_HOOK_PROVIDERS: set[type] = set()


class HookProvider(TableConfigProvider):
    """Marker-base for mixins / models that attach hooks to an AutoAPI router."""

    __autoapi_hooks__: list[Callable[["AutoAPI"], None]]

    @classmethod
    def append(cls, hook: Callable[["AutoAPI"], None]) -> None:
        cls.__autoapi_hooks__.append(hook)

    @classmethod
    def __autoapi_register_hooks__(cls, api: "AutoAPI") -> None:
        for hook in cls.__autoapi_hooks__:
            hook(api)

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        _HOOK_PROVIDERS.add(cls)
        cls.__autoapi_hooks__ = []


def list_hook_providers():
    return sorted(_HOOK_PROVIDERS, key=lambda c: c.__name__)
