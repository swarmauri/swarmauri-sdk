from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - forward ref
    from .. import AutoAPI


# ────────────────────────────────────────────────────────────────────
class _SchemaNS(SimpleNamespace):
    """Container namespace for generated Pydantic schemas."""

    def __init__(self, api: "AutoAPI"):
        super().__init__()
        self._api = api  # back-reference to parent
        self._name = "schemas"

    def __dir__(self) -> list[str]:  # pragma: no cover - passthrough
        return sorted(k for k in self.__dict__.keys() if not k.startswith("_"))
