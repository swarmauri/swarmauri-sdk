from __future__ import annotations

# autoapi/v3/bindings/schemas/utils.py

from types import SimpleNamespace
from typing import Any, Optional, Tuple, Type

from pydantic import BaseModel, create_model

from ...schema.types import SchemaArg, SchemaRef
from ...schema import namely_model


_Key = Tuple[str, str]  # (alias, target)


def _camel(s: str) -> str:
    return "".join(p.capitalize() or "_" for p in s.split("_"))


def _alias_schema(
    schema: Type[BaseModel], *, model: type, alias: str, kind: str
) -> Type[BaseModel]:
    name = f"{model.__name__}{_camel(alias)}{kind}"
    if getattr(schema, "__name__", None) == name:
        return schema
    try:
        clone = create_model(name, __base__=schema)  # type: ignore[arg-type]
    except Exception:  # pragma: no cover - best effort
        return schema
    return namely_model(
        clone,
        name=name,
        doc=f"{alias} {kind.lower()} schema for {model.__name__}",
    )


def _ensure_alias_namespace(model: type, alias: str) -> SimpleNamespace:
    ns = getattr(model.schemas, alias, None)
    if ns is None:
        ns = SimpleNamespace()
        setattr(model.schemas, alias, ns)
    return ns


def _pk_info(model: type) -> Tuple[str, type | Any]:
    """
    Return (pk_name, python_type) for single-PK tables. If composite, returns (pk, Any).
    """
    table = getattr(model, "__table__", None)
    if table is None or not getattr(table, "primary_key", None):
        return ("id", Any)
    cols = list(table.primary_key.columns)  # type: ignore[attr-defined]
    if not cols:
        return ("id", Any)
    if len(cols) > 1:
        # Composite keys: schema builder uses verb='delete' to require what's needed.
        # For bulk_delete we fall back to Any.
        return ("id", Any)
    col = cols[0]
    py_t = getattr(getattr(col, "type", None), "python_type", Any)
    return (getattr(col, "name", "id"), py_t or Any)


def _parse_str_ref(s: str) -> Tuple[str, str]:
    """
    Parse dotted schema ref "alias.in" | "alias.out".
    """
    s = s.strip()
    if "." not in s:
        raise ValueError(
            f"Invalid schema path '{s}', expected 'alias.in' or 'alias.out'"
        )
    alias, kind = s.split(".", 1)
    kind = kind.strip()
    if kind not in {"in", "out"}:
        raise ValueError(f"Invalid schema kind '{kind}', expected 'in' or 'out'")
    return alias.strip(), kind


def _resolve_schema_arg(model: type, arg: SchemaArg) -> Optional[Type[BaseModel]]:
    """
    Resolve an override to a concrete Pydantic model or raw:
      • SchemaRef("alias","in"|"out") → that model
      • "alias.in" | "alias.out"      → that model
      • "raw"                         → None (raw passthrough)
      • None                          → caller should keep defaults for canonical ops;
                                        for custom ops no defaults exist → raw
    Unsupported (will raise):
      • direct Pydantic model classes
      • callables/thunks
      • any other strings
    """
    if arg is None:
        return None

    # explicit raw
    if isinstance(arg, str) and arg.strip().lower() == "raw":
        return None

    # direct Pydantic model
    if isinstance(arg, type) and issubclass(arg, BaseModel):
        return arg

    # SchemaRef
    if isinstance(arg, SchemaRef):
        if arg.kind not in ("in", "out"):
            raise ValueError(
                f"Unsupported SchemaRef kind '{arg.kind}'. Use 'in' or 'out'."
            )
        ns = getattr(model, "schemas", None)
        if ns is None or getattr(ns, arg.alias, None) is None:
            raise KeyError(f"Unknown schema alias '{arg.alias}' on {model.__name__}")
        alias_ns = getattr(ns, arg.alias)
        attr = "in_" if arg.kind == "in" else "out"
        res = getattr(alias_ns, attr, None)
        if res is None:
            raise KeyError(f"Schema '{arg.alias}.{attr}' not found on {model.__name__}")
        return res  # type: ignore[return-value]

    # dotted string
    if isinstance(arg, str):
        alias, kind = _parse_str_ref(arg)
        ns = getattr(model, "schemas", None)
        if ns is None or getattr(ns, alias, None) is None:
            raise KeyError(f"Unknown schema alias '{alias}' on {model.__name__}")
        alias_ns = getattr(ns, alias)
        attr = "in_" if kind == "in" else "out"
        res = getattr(alias_ns, attr, None)
        if res is None:
            raise KeyError(f"Schema '{alias}.{attr}' not found on {model.__name__}")
        return res  # type: ignore[return-value]

    # Everything else is unsupported now
    raise TypeError(
        f"Unsupported SchemaArg type: {type(arg)}. "
        "Use SchemaRef(...,'in'|'out'), 'alias.in'/'alias.out', 'raw', or None."
    )
