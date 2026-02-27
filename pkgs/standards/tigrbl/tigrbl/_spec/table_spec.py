# tigrbl/tigrbl/v3/table/table_spec.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Optional, Sequence

from .._spec.engine_spec import EngineCfg
from .._spec.response_spec import ResponseSpec


@dataclass
class TableSpec:
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

    def __post_init__(self) -> None:
        # V4-style specs can pass a model import path while V3-style specs pass
        # the model class directly. Keep both surfaces available.
        if self.model is None and self.model_ref is not None:
            self.model = self.model_ref

    @classmethod
    def collect(cls, model: type) -> "TableSpec":
        from ..mapping.spec_normalization import merge_seq_attr, resolve_table_engine

        return cls(
            model=model,
            engine=resolve_table_engine(model),
            ops=merge_seq_attr(model, "OPS"),
            columns=merge_seq_attr(model, "COLUMNS"),
            schemas=merge_seq_attr(model, "SCHEMAS"),
            hooks=merge_seq_attr(model, "HOOKS"),
            security_deps=merge_seq_attr(model, "SECURITY_DEPS"),
            deps=merge_seq_attr(model, "DEPS"),
        )
