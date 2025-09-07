from __future__ import annotations
import logging

# autoapi/v3/bindings/schemas/utils.py

from types import SimpleNamespace
from typing import Any, Optional, Tuple, Type

from pydantic import BaseModel, create_model

from ...schema.types import SchemaArg, SchemaRef
from ...schema import namely_model

logging.getLogger("uvicorn").setLevel(logging.DEBUG)
logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/schemas/utils")


_Key = Tuple[str, str]  # (alias, target)


def _camel(s: str) -> str:
    return "".join(p.capitalize() or "_" for p in s.split("_"))


def _alias_schema(
    schema: Type[BaseModel], *, model: type, alias: str, kind: str
) -> Type[BaseModel]:
    name = f"{model.__name__}{_camel(alias)}{kind}"
    logger.debug("aliasing schema %s -> %s", getattr(schema, "__name__", None), name)
    if getattr(schema, "__name__", None) == name:
        logger.debug("schema already aliased: %s", name)
        return schema
    try:
        clone = create_model(name, __base__=schema)  # type: ignore[arg-type]
    except Exception:
        logger.debug("failed cloning schema %s", name, exc_info=True)
        return schema
    return namely_model(
        clone,
        name=name,
        doc=f"{alias} {kind.lower()} schema for {model.__name__}",
    )


def _ensure_alias_namespace(model: type, alias: str) -> SimpleNamespace:
    ns = getattr(model.schemas, alias, None)
    if ns is None:
        logger.debug("creating namespace for %s.%s", model.__name__, alias)
        ns = SimpleNamespace()
        setattr(model.schemas, alias, ns)
    else:
        logger.debug("reusing namespace for %s.%s", model.__name__, alias)
    return ns


def _pk_info(model: type) -> Tuple[str, type | Any]:
    """
    Return (pk_name, python_type) for single-PK tables. If composite, returns (pk, Any).
    """
    table = getattr(model, "__table__", None)
    if table is None or not getattr(table, "primary_key", None):
        logger.debug("no table or pk for %s", model)
        return ("id", Any)
    cols = list(table.primary_key.columns)  # type: ignore[attr-defined]
    if not cols:
        logger.debug("no pk columns for %s", model)
        return ("id", Any)
    if len(cols) > 1:
        logger.debug("composite pk for %s", model)
        # Composite keys: schema builder uses verb='delete' to require what's needed.
        # For bulk_delete we fall back to Any.
        return ("id", Any)
    col = cols[0]
    py_t = getattr(getattr(col, "type", None), "python_type", Any)
    name = getattr(col, "name", "id")
    logger.debug("pk info for %s -> %s", model, name)
    return (name, py_t or Any)


def _parse_str_ref(s: str) -> Tuple[str, str]:
    """
    Parse dotted schema ref "alias.in" | "alias.out".
    """
    s = s.strip()
    if "." not in s:
        logger.debug("invalid schema ref: %s", s)
        raise ValueError(
            f"Invalid schema path '{s}', expected 'alias.in' or 'alias.out'"
        )
    alias, kind = s.split(".", 1)
    kind = kind.strip()
    if kind not in {"in", "out"}:
        logger.debug("invalid schema kind in ref: %s", kind)
        raise ValueError(f"Invalid schema kind '{kind}', expected 'in' or 'out'")
    logger.debug("parsed schema ref: alias=%s kind=%s", alias.strip(), kind)
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
    logger.debug("resolving schema arg %s on %s", arg, model)
    if arg is None:
        logger.debug("arg is None -> keep default")
        return None

    # explicit raw
    if isinstance(arg, str) and arg.strip().lower() == "raw":
        logger.debug("arg explicitly raw")
        return None

    # direct Pydantic model
    if isinstance(arg, type) and issubclass(arg, BaseModel):
        logger.debug("arg is direct model %s", arg)
        return arg

    # SchemaRef
    if isinstance(arg, SchemaRef):
        logger.debug("arg is SchemaRef %s", arg)
        if arg.kind not in ("in", "out"):
            logger.debug("unsupported SchemaRef kind %s", arg.kind)
            raise ValueError(
                f"Unsupported SchemaRef kind '{arg.kind}'. Use 'in' or 'out'."
            )
        ns = getattr(model, "schemas", None)
        if ns is None or getattr(ns, arg.alias, None) is None:
            logger.debug("unknown schema alias %s on %s", arg.alias, model)
            raise KeyError(f"Unknown schema alias '{arg.alias}' on {model.__name__}")
        alias_ns = getattr(ns, arg.alias)
        attr = "in_" if arg.kind == "in" else "out"
        res = getattr(alias_ns, attr, None)
        if res is None:
            logger.debug("schema %s.%s missing on %s", arg.alias, attr, model)
            raise KeyError(f"Schema '{arg.alias}.{attr}' not found on {model.__name__}")
        logger.debug("resolved SchemaRef to %s", res)
        return res  # type: ignore[return-value]

    # dotted string
    if isinstance(arg, str):
        logger.debug("arg is dotted string %s", arg)
        alias, kind = _parse_str_ref(arg)
        ns = getattr(model, "schemas", None)
        if ns is None or getattr(ns, alias, None) is None:
            logger.debug("unknown schema alias %s on %s", alias, model)
            raise KeyError(f"Unknown schema alias '{alias}' on {model.__name__}")
        alias_ns = getattr(ns, alias)
        attr = "in_" if kind == "in" else "out"
        res = getattr(alias_ns, attr, None)
        if res is None:
            logger.debug("schema %s.%s missing on %s", alias, attr, model)
            raise KeyError(f"Schema '{alias}.{attr}' not found on {model.__name__}")
        logger.debug("resolved dotted ref to %s", res)
        return res  # type: ignore[return-value]

    # Everything else is unsupported now
    logger.debug("unsupported schema arg type %s", type(arg))
    raise TypeError(
        f"Unsupported SchemaArg type: {type(arg)}. "
        "Use SchemaRef(...,'in'|'out'), 'alias.in'/'alias.out', 'raw', or None."
    )
