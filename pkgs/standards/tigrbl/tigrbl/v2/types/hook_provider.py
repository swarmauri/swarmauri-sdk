# tigrbl/v2/types/hook_provider.py  – tiny helper module
from abc import abstractmethod
from typing import TYPE_CHECKING

from .table_config_provider import TableConfigProvider

if TYPE_CHECKING:  # forward ref avoids circular import
    from tigrbl.v2 import Tigrbl

_HOOK_PROVIDERS: set[type] = set()


class HookProvider(TableConfigProvider):
    """
    Marker-base for mixins / models that attach hooks to an Tigrbl router.

    Subclasses **must** implement `__tigrbl_register_hooks__`.
    """

    @classmethod
    @abstractmethod
    def __tigrbl_register_hooks__(cls, api: "Tigrbl") -> None: ...

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        _HOOK_PROVIDERS.add(cls)


def list_hook_providers():
    return sorted(_HOOK_PROVIDERS, key=lambda c: c.__name__)
