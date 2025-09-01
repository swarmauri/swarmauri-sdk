# autoapi/autoapi/v3/table/shortcuts.py
from __future__ import annotations

from typing import Any, Sequence, Type

from .table_spec import TableSpec
from ._table import Table


def defineTableSpec(
    *,
    # engine binding
    db: Any = None,
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
    Build a Table spec class with class attributes only (no instances).
    Use directly in your ORM class MRO:

        class User(defineTableSpec(db=..., ops=(...)), Base, Table):
            __tablename__ = "users"

    or pass it to ``deriveTable(Model, ...)`` to get a configured subclass.
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

    # Engine binding is conventionally stored under table_config["db"]
    # so existing collectors/autowiring can find it consistently.
    if db is not None:
        attrs["table_config"] = {"db": db}

    return type("TableSpec", (TableSpec,), attrs)


def deriveTable(model: Type[Table], **kw: Any) -> Type[Table]:
    """Produce a concrete ORM subclass that inherits the spec."""
    Spec = defineTableSpec(**kw)
    name = f"{model.__name__}WithSpec"
    return type(name, (Spec, model), {})


__all__ = ["defineTableSpec", "deriveTable"]
