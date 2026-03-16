from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Sequence

from .._spec.app_spec import merge_seq_attr
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

    @classmethod
    def collect(cls, router: type) -> "RouterSpec":
        sentinel = object()
        name: Any = sentinel
        prefix: Any = sentinel
        engine: Any = sentinel
        response: Any = sentinel

        for base in router.__mro__:
            if "NAME" in base.__dict__ and name is sentinel:
                name = base.__dict__["NAME"]
            if "PREFIX" in base.__dict__ and prefix is sentinel:
                prefix = base.__dict__["PREFIX"]
            if "ENGINE" in base.__dict__ and engine is sentinel:
                engine = base.__dict__["ENGINE"]
            if "RESPONSE" in base.__dict__ and response is sentinel:
                response = base.__dict__["RESPONSE"]

        if name is sentinel:
            name = getattr(router, "__name__", "router").lower()
        if prefix is sentinel:
            prefix = ""
        if engine is sentinel:
            engine = None
        if response is sentinel:
            response = None

        return cls(
            name=str(name or "router"),
            prefix=str(prefix or ""),
            engine=engine,
            tags=merge_seq_attr(router, "TAGS", include_inherited=True),
            ops=merge_seq_attr(router, "OPS", include_inherited=True),
            tables=merge_seq_attr(router, "TABLES", include_inherited=True),
            schemas=merge_seq_attr(router, "SCHEMAS", include_inherited=True),
            hooks=merge_seq_attr(router, "HOOKS", include_inherited=True),
            deps=merge_seq_attr(router, "DEPS", include_inherited=True),
            security_deps=merge_seq_attr(
                router, "SECURITY_DEPS", include_inherited=True
            ),
            response=response,
        )
