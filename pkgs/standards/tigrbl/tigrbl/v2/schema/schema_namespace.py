from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - forward ref
    from .. import Tigrbl


# ────────────────────────────────────────────────────────────────────
class _SchemaNS(SimpleNamespace):
    """
    Attribute-style access to generated Pydantic schemas.

        api.schemas.UserCreateIn         → <class 'UserCreate'>
        api.schemas.UserCreateIn(name=…) → instance of that model
    """

    def __init__(self, api: "Tigrbl"):
        super().__init__()
        self._api = api  # back-reference to parent

    def __dir__(self) -> list[str]:
        """Expose only operation-specific schema names."""
        return sorted(self._api._schemas.keys())

    def __getattr__(self, item: str):  # lazy lookup / build
        try:
            return self.__dict__[item]
        except KeyError:
            pass
        if item in self._api._schemas:
            mdl = self._api._schemas[item]
            setattr(self, item, mdl)
            return mdl
        raise AttributeError(item) from None
