from __future__ import annotations
import logging

# tigrbl/v3/bindings/schemas/utils.py

from types import SimpleNamespace
from typing import Any, Optional, Tuple, Type

from pydantic import BaseModel, create_model

from ...schema.types import SchemaArg, SchemaRef
from ...schema import namely_model

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/schemas/utils")

_Key = Tuple[str, str]  # (alias, target)


def _camel(s: str) -> str:
    return "".join(p.capitalize() or "_" for p in s.split("_"))


def _alias_schema(
    schema: Type[BaseModel], *, model: type, alias: str, kind: str
) -> Type[BaseModel]:
    logger.debug(
        "Aliasing schema %s for %s as %s %s",
        schema.__name__,
        model.__name__,
        alias,
        kind,
    )
    name = f"{model.__name__}{_camel(alias)}{kind}"
    if getattr(schema, "__name__", None) == name:
        logger.debug("Schema already aliased as %s", name)
        return schema
    try:
        clone = create_model(name, __base__=schema)  # type: ignore[arg-type]
    except Exception as e:  # pragma: no cover - best effort
        logger.debug("Failed to clone schema %s: %s", schema.__name__, e)
        return schema
    logger.debug("Created alias schema %s", name)
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
        logger.debug("Created namespace for %s.%s", model.__name__, alias)
    else:
        logger.debug("Using existing namespace for %s.%s", model.__name__, alias)
    return ns


def _pk_info(model: type) -> Tuple[str, type | Any]:
    """
    Return (pk_name, python_type) for single-PK tables. If composite, returns (pk, Any).
    """
    table = getattr(model, "__table__", None)
    if table is None or not getattr(table, "primary_key", None):
        logger.debug("Model %s has no table or primary key", model.__name__)
        return ("id", Any)
    cols = list(table.primary_key.columns)  # type: ignore[attr-defined]
    if not cols:
        logger.debug("Model %s primary key columns empty", model.__name__)
        return ("id", Any)
    if len(cols) > 1:
        logger.debug("Model %s has composite primary key", model.__name__)
        # Composite keys: schema builder uses verb='delete' to require what's needed.
        # For bulk_delete we fall back to Any.
        return ("id", Any)
    col = cols[0]
    py_t = getattr(getattr(col, "type", None), "python_type", Any)
    logger.debug(
        "Model %s primary key %s of type %s",
        model.__name__,
        getattr(col, "name", "id"),
        py_t,
    )
    return (getattr(col, "name", "id"), py_t or Any)


def _parse_str_ref(s: str) -> Tuple[str, str]:
    """
    Parse dotted schema ref "alias.in" | "alias.out".
    """
    s = s.strip()
    logger.debug("Parsing schema ref '%s'", s)
    if "." not in s:
        logger.debug("Schema ref '%s' missing '.'", s)
        raise ValueError(
            f"Invalid schema path '{s}', expected 'alias.in' or 'alias.out'"
        )
    alias, kind = s.split(".", 1)
    kind = kind.strip()
    if kind not in {"in", "out"}:
        logger.debug("Schema ref '%s' has invalid kind '%s'", s, kind)
        raise ValueError(f"Invalid schema kind '{kind}', expected 'in' or 'out'")
    logger.debug("Parsed schema ref alias=%s kind=%s", alias, kind)
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
    logger.debug("Resolving schema arg %s for %s", arg, model.__name__)
    if arg is None:
        logger.debug("Schema arg is None; returning None")
        return None

    # explicit raw
    if isinstance(arg, str) and arg.strip().lower() == "raw":
        logger.debug("Schema arg is explicit raw")
        return None

    # direct Pydantic model
    if isinstance(arg, type) and issubclass(arg, BaseModel):
        logger.debug("Schema arg is direct model %s", arg.__name__)
        return arg

    # SchemaRef
    if isinstance(arg, SchemaRef):
        logger.debug("Schema arg is SchemaRef(alias=%s, kind=%s)", arg.alias, arg.kind)
        if arg.kind not in ("in", "out"):
            logger.debug("Unsupported SchemaRef kind '%s'", arg.kind)
            raise ValueError(
                f"Unsupported SchemaRef kind '{arg.kind}'. Use 'in' or 'out'.",
            )
        ns = getattr(model, "schemas", None)
        if ns is None or getattr(ns, arg.alias, None) is None:
            logger.debug("Unknown schema alias '%s' on %s", arg.alias, model.__name__)
            raise KeyError(f"Unknown schema alias '{arg.alias}' on {model.__name__}")
        alias_ns = getattr(ns, arg.alias)
        attr = "in_" if arg.kind == "in" else "out"
        res = getattr(alias_ns, attr, None)
        if res is None:
            logger.debug(
                "Schema '%s.%s' not found on %s", arg.alias, attr, model.__name__
            )
            raise KeyError(f"Schema '{arg.alias}.{attr}' not found on {model.__name__}")
        logger.debug(
            "Resolved SchemaRef %s.%s to %s",
            arg.alias,
            attr,
            getattr(res, "__name__", None),
        )
        return res  # type: ignore[return-value]

    # dotted string
    if isinstance(arg, str):
        alias, kind = _parse_str_ref(arg)
        ns = getattr(model, "schemas", None)
        if ns is None or getattr(ns, alias, None) is None:
            logger.debug("Unknown schema alias '%s' on %s", alias, model.__name__)
            raise KeyError(f"Unknown schema alias '{alias}' on {model.__name__}")
        alias_ns = getattr(ns, alias)
        attr = "in_" if kind == "in" else "out"
        res = getattr(alias_ns, attr, None)
        if res is None:
            logger.debug("Schema '%s.%s' not found on %s", alias, attr, model.__name__)
            raise KeyError(f"Schema '{alias}.{attr}' not found on {model.__name__}")
        logger.debug(
            "Resolved schema path %s.%s to %s",
            alias,
            attr,
            getattr(res, "__name__", None),
        )
        return res  # type: ignore[return-value]

    logger.debug("Unsupported SchemaArg type: %s", type(arg))
    # Everything else is unsupported now
    raise TypeError(
        f"Unsupported SchemaArg type: {type(arg)}. "
        "Use SchemaRef(...,'in'|'out'), 'alias.in'/'alias.out', 'raw', or None.",
    )
