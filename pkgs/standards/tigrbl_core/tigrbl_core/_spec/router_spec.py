from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Sequence

from .._spec.engine_spec import EngineCfg
from .._spec.op_spec import OpSpec
from .._spec.response_spec import ResponseSpec
from .._spec.schema_spec import SchemaSpec
from .._spec.table_spec import TableSpec
from .serde import SerdeMixin


@dataclass
class RouterSpec(SerdeMixin):
    """Used to produce a router subclass via Router.from_spec()."""

    name: str = "router"
    prefix: str = ""
    engine: Optional[EngineCfg] = None
    tags: Sequence[str] = field(default_factory=tuple)
    ops: Sequence[Any] = field(default_factory=tuple)
    schemas: Sequence[Any] = field(default_factory=tuple)
    hooks: Sequence[Callable[..., Any]] = field(default_factory=tuple)
    security_deps: Sequence[Callable[..., Any]] = field(default_factory=tuple)
    deps: Sequence[Callable[..., Any]] = field(default_factory=tuple)
    response: Optional[ResponseSpec] = None
    tables: Sequence[Any] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        self._validate_nested_specs("tables", self.tables, (TableSpec,))
        self._validate_nested_specs("ops", self.ops, (OpSpec,))
        self._validate_nested_specs("schemas", self.schemas, (SchemaSpec,))

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RouterSpec":
        if "models" in payload:
            raise ValueError(
                "RouterSpec does not accept 'models'; use 'tables' with nested TableSpec values."
            )
        return super().from_dict(payload)

    @staticmethod
    def _validate_nested_specs(
        field_name: str,
        values: Sequence[Any],
        expected_types: tuple[type[Any], ...],
    ) -> None:
        for value in values:
            if isinstance(value, str):
                raise TypeError(
                    f"RouterSpec.{field_name} entries must be nested specs, not strings."
                )
            if not isinstance(value, expected_types):
                expected = ", ".join(t.__name__ for t in expected_types)
                raise TypeError(
                    f"RouterSpec.{field_name} entries must be {expected}; got {type(value).__name__}."
                )
