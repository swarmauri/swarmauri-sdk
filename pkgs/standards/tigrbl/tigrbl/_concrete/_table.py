# tigrbl/tigrbl/v3/table/_table.py
from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Callable, Mapping

from .._concrete._engine import AsyncSession, Session
from ..ddl import initialize as _ddl_initialize
from ..engine import install_from_objects  # reuse the collector
from ..mapping import engine_resolver as _resolver
from ..specs.table_spec import TableSpec
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
        allowed = (cls.DEFAULT_CANON_VERBS | inc) - exc
        return op in allowed

    @staticmethod
    def _merge_seq_attr(model: type, attr: str) -> tuple[Any, ...]:
        values: list[Any] = []
        for base in model.__mro__:
            seq = base.__dict__.get(attr, ()) or ()
            try:
                values.extend(seq)
            except TypeError:  # pragma: no cover - non-iterable
                values.append(seq)
        return tuple(values)

    @classmethod
    def _collect_mro_spec(cls) -> TableSpec:
        direct_engine: Any | None = None
        inherited_engine: Any | None = None

        for base in cls.__mro__:
            if "table_config" in base.__dict__:
                cfg = base.__dict__.get("table_config")
                if isinstance(cfg, Mapping):
                    eng = (
                        cfg.get("engine")
                        or cfg.get("db")
                        or cfg.get("database")
                        or cfg.get("engine_provider")
                        or cfg.get("db_provider")
                    )
                    if eng is not None and direct_engine is None:
                        direct_engine = eng
                continue

            cfg = getattr(base, "table_config", None)
            if isinstance(cfg, Mapping):
                eng = (
                    cfg.get("engine")
                    or cfg.get("db")
                    or cfg.get("database")
                    or cfg.get("engine_provider")
                    or cfg.get("db_provider")
                )
                if eng is not None:
                    inherited_engine = eng

        engine = inherited_engine if inherited_engine is not None else direct_engine

        return TableSpec(
            model=cls,
            engine=engine,
            ops=cls._merge_seq_attr(cls, "OPS"),
            columns=cls._merge_seq_attr(cls, "COLUMNS"),
            schemas=cls._merge_seq_attr(cls, "SCHEMAS"),
            hooks=cls._merge_seq_attr(cls, "HOOKS"),
            security_deps=cls._merge_seq_attr(cls, "SECURITY_DEPS"),
            deps=cls._merge_seq_attr(cls, "DEPS"),
        )

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
            install_from_objects(tables=[cls])
        except Exception:  # pragma: no cover - best effort
            pass

    @classmethod
    def install_engines(cls, *, router: Any | None = None) -> None:
        install_from_objects(router=router, tables=[cls])

    @classmethod
    def acquire(
        cls, *, op_alias: str | None = None
    ) -> tuple[Session | AsyncSession, Callable[[], None]]:
        db, release = _resolver.acquire(model=cls, op_alias=op_alias)
        return db, release

    initialize = classmethod(_ddl_initialize)
