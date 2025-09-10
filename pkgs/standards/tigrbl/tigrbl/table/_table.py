# tigrbl/tigrbl/v3/table/_table.py
from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Callable

from ..engine._engine import AsyncSession, Session
from ..engine import install_from_objects  # reuse the collector
from ..engine import resolver as _resolver
from ..ddl import initialize as _ddl_initialize
from ._base import Base
from .table_spec import TableSpec


class Table(Base, TableSpec):
    """Declarative ORM table base.

    This class now integrates :class:`Base` so ORM models and tables share
    the same type.  Column specifications are exposed via ``columns`` for
    convenience.
    """

    __abstract__ = True
    columns: SimpleNamespace = SimpleNamespace()

    def __init__(self, **kw: Any) -> None:  # pragma: no cover - SQLA sets attrs
        for k, v in kw.items():
            setattr(self, k, v)

    def __init_subclass__(cls, **kw: Any) -> None:  # noqa: D401
        super().__init_subclass__(**kw)

        # expose ColumnSpecs under `columns` namespace
        specs = getattr(cls, "__tigrbl_cols__", {})
        cls.columns = SimpleNamespace(**specs)

        # auto-register table-level bindings if declared
        try:
            install_from_objects(models=[cls])
        except Exception:  # pragma: no cover - best effort
            pass

    @classmethod
    def install_engines(cls, *, api: Any | None = None) -> None:
        install_from_objects(api=api, models=[cls])

    @classmethod
    def acquire(
        cls, *, op_alias: str | None = None
    ) -> tuple[Session | AsyncSession, Callable[[], None]]:
        db, release = _resolver.acquire(model=cls, op_alias=op_alias)
        return db, release

    initialize = classmethod(_ddl_initialize)
