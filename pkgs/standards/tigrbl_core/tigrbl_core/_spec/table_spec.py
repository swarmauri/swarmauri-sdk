# pkgs/standards/tigrbl_core/tigrbl/_spec/table_spec.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Optional, Sequence

from .._spec.app_spec import merge_seq_attr
from .._spec.engine_spec import EngineCfg
from .._spec.response_spec import ResponseSpec
from .serde import SerdeMixin


def resolve_table_engine(model: type) -> Any | None:
    """Resolve a table engine with wrapper-precedence semantics."""

    resolved_engine: Any | None = None
    for base in model.__mro__:
        cfg = base.__dict__.get("table_config")
        if not isinstance(cfg, Mapping):
            continue
        eng = (
            cfg.get("engine")
            or cfg.get("db")
            or cfg.get("database")
            or cfg.get("engine_provider")
            or cfg.get("db_provider")
        )
        if eng is not None:
            resolved_engine = eng

    if resolved_engine is not None:
        return resolved_engine

    cfg = getattr(model, "table_config", None)
    if isinstance(cfg, Mapping):
        return (
            cfg.get("engine")
            or cfg.get("db")
            or cfg.get("database")
            or cfg.get("engine_provider")
            or cfg.get("db_provider")
        )
    return None


@dataclass
class TableSpec(SerdeMixin):
    """
    Declarative enrichments for an ORM class (model == table).
    This does not construct an instance; it decorates/produces a class.
    """

    model: Any | None = None  # ORM class
    model_ref: str | None = None  # import string (e.g. "mypkg.models:Model")
    engine: Optional[EngineCfg] = None

    # NEW
    ops: Sequence[Any] = field(default_factory=tuple)  # OpSpec or shorthands
    columns: Sequence[Any] | Mapping[str, Any] = field(
        default_factory=tuple
    )  # ColumnSpec or shorthands
    schemas: Sequence[Any] = field(default_factory=tuple)
    hooks: Sequence[Callable[..., Any]] = field(default_factory=tuple)
    security_deps: Sequence[Callable[..., Any]] = field(default_factory=tuple)
    deps: Sequence[Callable[..., Any]] = field(default_factory=tuple)

    response: Optional[ResponseSpec] = None

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        cls.OPS = tuple(merge_seq_attr(cls, "OPS", include_inherited=True))
        cls.COLUMNS = tuple(merge_seq_attr(cls, "COLUMNS", include_inherited=True))
        cls.SCHEMAS = tuple(merge_seq_attr(cls, "SCHEMAS", include_inherited=True))
        cls.HOOKS = tuple(merge_seq_attr(cls, "HOOKS", include_inherited=True))
        cls.SECURITY_DEPS = tuple(
            merge_seq_attr(cls, "SECURITY_DEPS", include_inherited=True)
        )
        cls.DEPS = tuple(merge_seq_attr(cls, "DEPS", include_inherited=True))

        engine = resolve_table_engine(cls)
        if engine is not None:
            cfg = dict(getattr(cls, "table_config", {}) or {})
            cfg.setdefault("engine", engine)
            cls.table_config = cfg

    def __post_init__(self) -> None:
        # V4-style specs can pass a model import path while V3-style specs pass
        # the model class directly. Keep both surfaces available.
        if self.model is None and self.model_ref is not None:
            self.model = self.model_ref

    @classmethod
    def collect(cls, model: type) -> "TableSpec":
        return cls(
            model=model,
            engine=resolve_table_engine(model),
            ops=merge_seq_attr(model, "OPS", include_inherited=True),
            columns=merge_seq_attr(model, "COLUMNS", include_inherited=True),
            schemas=merge_seq_attr(model, "SCHEMAS", include_inherited=True),
            hooks=merge_seq_attr(model, "HOOKS", include_inherited=True),
            security_deps=merge_seq_attr(
                model, "SECURITY_DEPS", include_inherited=True
            ),
            deps=merge_seq_attr(model, "DEPS", include_inherited=True),
        )
