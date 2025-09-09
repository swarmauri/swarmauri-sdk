# tigrbl/v3/types/authn_abc.py
from __future__ import annotations
from abc import ABC, abstractmethod
from fastapi import Request


class AuthNProvider(ABC):
    """
    Marker‑interface that any AuthN extension must implement
    so that Tigrbl can plug itself in at run‑time.
    """

    # ---------- FastAPI dependency ----------
    @abstractmethod
    async def get_principal(self, request: Request):  # -> dict[str, str]
        """Return {"sub": user_id, "tid": tenant_id, ...} or raise HTTP 401."""


__all__ = ["AuthNProvider"]


for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]


def __dir__():
    """Tighten ``dir()`` output for interactive sessions."""

    return sorted(__all__)
