# autoapi/v2/types/hook_provider.py  – tiny helper module
from abc import abstractmethod
from typing import TYPE_CHECKING

from .table_config_provider import TableConfigProvider

if TYPE_CHECKING:  # forward ref avoids circular import
    from autoapi.v2 import AutoAPI

_HOOK_PROVIDERS: set[type] = set()


class HookProvider(TableConfigProvider):
    """
    Marker-base for mixins / models that attach hooks to an AutoAPI router.

    Subclasses **must** implement `__autoapi_register_hooks__`.
    """

    @classmethod
    @abstractmethod
    def __autoapi_register_hooks__(cls, api: "AutoAPI") -> None: ...

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        _HOOK_PROVIDERS.add(cls)


def list_hook_providers():
    return sorted(_HOOK_PROVIDERS, key=lambda c: c.__name__)
