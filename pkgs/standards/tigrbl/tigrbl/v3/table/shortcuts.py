# tigrbl/tigrbl/v3/table/shortcuts.py
from __future__ import annotations

from typing import Any, Sequence, Type

from .table_spec import TableSpec
from ._table import Table


def defineTableSpec(
    *,
    # engine binding
    engine: Any = None,
    # composition
    ops: Sequence[Any] = (),
    columns: Sequence[Any] = (),
    schemas: Sequence[Any] = (),
    hooks: Sequence[Any] = (),
    # dependency stacks
    security_deps: Sequence[Any] = (),
    deps: Sequence[Any] = (),
) -> Type[TableSpec]:
    """
    Build a Table-spec class with class attributes only (no instances).
    Use directly in your ORM class MRO:

        class User(defineTableSpec(engine=..., ops=(...)), Base, Table):
            __tablename__ = "users"

    or pass it to `deriveTable(Model, ...)` to get a configured subclass.
    """
    attrs = {
        # top-level mirrors read by collectors
        "OPS": tuple(ops or ()),
        "COLUMNS": tuple(columns or ()),
        "SCHEMAS": tuple(schemas or ()),
        "HOOKS": tuple(hooks or ()),
        "SECURITY_DEPS": tuple(security_deps or ()),
        "DEPS": tuple(deps or ()),
    }

    # Engine binding is conventionally stored under table_config["engine"]
    # (and legacy "db" for backward compatibility) so collectors can find it.
    if engine is not None:
        attrs["table_config"] = {"engine": engine, "db": engine}

    return type("TableSpec", (TableSpec,), attrs)


def deriveTable(model: Type[Table], **kw: Any) -> Type[Table]:
    """Produce a concrete ORM subclass that inherits the spec."""
    Spec = defineTableSpec(**kw)
    name = f"{model.__name__}WithSpec"
    return type(name, (Spec, model), {})


__all__ = ["defineTableSpec", "deriveTable"]
