# autoapi/autoapi/v3/table/_table.py
from __future__ import annotations

from typing import Any

from ..engines import resolver as _resolver
from ..engine import install_from_objects  # reuse the collector
from .table_spec import TableSpec


class Table(TableSpec):
    def __init_subclass__(cls, **kw: Any) -> None:
        super().__init_subclass__(**kw)
        # auto-register table-level bindings if declared
        try:
            install_from_objects(models=[cls])
        except Exception:
            pass

    @classmethod
    def install_engines(cls, *, api: Any | None = None) -> None:
        install_from_objects(api=api, models=[cls])

    @classmethod
    def acquire(cls, *, op_alias: str | None = None):
        db, release = _resolver.acquire(model=cls, op_alias=op_alias)
        return db, release
