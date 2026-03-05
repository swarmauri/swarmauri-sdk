# tigrbl/tigrbl/v3/table/_table.py
from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Callable

from .._concrete._engine import AsyncSession, Session
from ..ddl import initialize as _ddl_initialize
from .._concrete._engine import Engine  # reuse the collector
from ..mapping import engine_resolver as _resolver
from .._spec.table_spec import TableSpec
from .._base._table_base import TableBase


class Table(TableBase):
    """Declarative ORM table base.

    This class now integrates :class:`TableBase` so ORM models and tables share
    the same type. Column specifications are exposed via ``columns`` for
    convenience.
    """

    __abstract__ = True
    columns: SimpleNamespace = SimpleNamespace()

    DEFAULT_CANON_VERBS = {
        "create",
        "read",
        "update",
        "replace",
        "delete",
        "list",
        "clear",
    }

    @classmethod
    def should_wire_canonical(cls, op: str) -> bool:
        from ..config.constants import (
            TIGRBL_DEFAULTS_EXCLUDE_ATTR,
            TIGRBL_DEFAULTS_INCLUDE_ATTR,
            TIGRBL_DEFAULTS_MODE_ATTR,
        )

        mode = getattr(cls, TIGRBL_DEFAULTS_MODE_ATTR, "all")
        inc = set(getattr(cls, TIGRBL_DEFAULTS_INCLUDE_ATTR, set()))
        exc = set(getattr(cls, TIGRBL_DEFAULTS_EXCLUDE_ATTR, set()))
        if mode == "none":
            return False
        if mode == "some":
            return op in inc
        default_verbs = set(
            getattr(cls, "DEFAULT_CANON_VERBS", Table.DEFAULT_CANON_VERBS)
        )
        allowed = (default_verbs | inc) - exc
        return op in allowed

    @classmethod
    def _collect_mro_spec(cls) -> TableSpec:
        return TableSpec.collect(cls)

    def __init__(self, **kw: Any) -> None:  # pragma: no cover - SQLA sets attrs
        for k, v in kw.items():
            setattr(self, k, v)

    def __init_subclass__(cls, **kw: Any) -> None:  # noqa: D401
        super().__init_subclass__(**kw)

        collected_spec = cls._collect_mro_spec()

        cls.OPS = tuple(collected_spec.ops)
        cls.COLUMNS = tuple(collected_spec.columns)
        cls.SCHEMAS = tuple(collected_spec.schemas)
        cls.HOOKS = tuple(collected_spec.hooks)
        cls.SECURITY_DEPS = tuple(collected_spec.security_deps)
        cls.DEPS = tuple(collected_spec.deps)

        if collected_spec.engine is not None:
            cfg = dict(getattr(cls, "table_config", {}) or {})
            cfg.setdefault("engine", collected_spec.engine)
            cls.table_config = cfg

        # expose ColumnSpecs under `columns` namespace
        specs = getattr(cls, "__tigrbl_cols__", {})
        cls.columns = SimpleNamespace(**specs)

        # auto-register table-level bindings if declared
        try:
            Engine.install_from_objects(tables=(cls,))
        except Exception:  # pragma: no cover - best effort
            pass

    @classmethod
    def install_engines(cls, *, router: Any | None = None) -> None:
        Engine.install_from_objects(router=router, tables=(cls,))

    @classmethod
    def acquire(
        cls, *, op_alias: str | None = None
    ) -> tuple[Session | AsyncSession, Callable[[], None]]:
        db, release = _resolver.acquire(model=cls, op_alias=op_alias)
        return db, release

    initialize = classmethod(_ddl_initialize)
