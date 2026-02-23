# tigrbl/tigrbl/v3/op/_op.py
from __future__ import annotations

from dataclasses import replace
from typing import Any

from .types import OpSpec


class Op(OpSpec):
    """Declarative operation descriptor with optional engine binding."""

    __slots__ = ()

    def __set_name__(self, owner: type, name: str) -> None:  # noqa: D401
        spec = self
        alias = self.alias or name
        if self.table is not owner or self.alias != alias:
            spec = replace(self, table=owner, alias=alias)
        ops = list(getattr(owner, "__tigrbl_ops__", ()) or [])
        ops.append(spec)
        owner.__tigrbl_ops__ = tuple(ops)

    def install_engines(
        self, *, api: Any | None = None, model: type | None = None
    ) -> None:
        from ..engine import install_from_objects

        m = model if model is not None else self.table
        if m is not None:
            install_from_objects(api=api, models=[m])
