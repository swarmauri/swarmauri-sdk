# autoapi/v3/bindings/schemas.py
from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type

from pydantic import BaseModel, Field, RootModel, ConfigDict, create_model

from ..opspec import OpSpec
from ..opspec.types import (
    SchemaRef,
    SchemaArg,
)  # lazy-capable schema args (runtime: we restrict forms)
from ..schema import _build_schema, _build_list_params, namely_model
from ..decorators import collect_decorated_schemas  # ← seed @schema_ctx declarations

logger = logging.getLogger(__name__)

_Key = Tuple[str, str]  # (alias, target)

# ───────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ───────────────────────────────────────────────────────────────────────────────


def _camel(s: str) -> str:
    return "".join(p.capitalize() or "_" for p in s.split("_"))


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


def _make_bulk_rows_model(
    model: type, verb: str, item_schema: Type[BaseModel]
) -> Type[BaseModel]:
    """
    Build a root model representing `List[item_schema]`.
    """
    name = f"{model.__name__}{_camel(verb)}Request"
    example = _extract_example(item_schema)
    examples = [[example]] if example else []

    item_ref = {"$ref": f"#/components/schemas/{item_schema.__name__}"}

    class _BulkModel(RootModel[List[item_schema]]):  # type: ignore[misc]
        model_config = ConfigDict(
            json_schema_extra={"examples": examples, "items": item_ref}
        )

    return namely_model(
        _BulkModel,
        name=name,
        doc=f"{verb} request schema for {model.__name__}",
    )


def _make_bulk_rows_response_model(
    model: type, verb: str, item_schema: Type[BaseModel]
) -> Type[BaseModel]:
    """Build a root model representing ``List[item_schema]`` for responses."""
    name = f"{model.__name__}{_camel(verb)}Response"
    example = _extract_example(item_schema)
    examples = [[example]] if example else []

    item_ref = {"$ref": f"#/components/schemas/{item_schema.__name__}"}

    class _BulkModel(RootModel[List[item_schema]]):  # type: ignore[misc]
        model_config = ConfigDict(
            json_schema_extra={"examples": examples, "items": item_ref}
        )

    return namely_model(
        _BulkModel,
        name=name,
        doc=f"{verb} response schema for {model.__name__}",
    )


def _make_bulk_ids_model(
    model: type, verb: str, pk_type: type | Any
) -> Type[BaseModel]:
    """
    Build a wrapper schema with an `ids: List[pk_type]` field.
    """
    name = f"{model.__name__}{_camel(verb)}Request"
    schema = create_model(  # type: ignore[call-arg]
        name,
        ids=(List[pk_type], Field(...)),  # type: ignore[name-defined]
    )
    return namely_model(
        schema,
        name=name,
        doc=f"{verb} request schema for {model.__name__}",
    )


def _make_deleted_response_model(model: type, verb: str) -> Type[BaseModel]:
    """Build a response schema with a ``deleted`` count."""
    name = f"{model.__name__}{_camel(verb)}Response"
    schema = create_model(  # type: ignore[call-arg]
        name,
        deleted=(int, Field(..., examples=[0])),
        __config__=ConfigDict(json_schema_extra={"examples": [{"deleted": 0}]}),
    )
    return namely_model(
        schema,
        name=name,
        doc=f"{verb} response schema for {model.__name__}",
    )


def _make_pk_model(
    model: type, verb: str, pk_name: str, pk_type: type | Any
) -> Type[BaseModel]:
    """Build a wrapper schema with a single primary-key field."""
    name = f"{model.__name__}{_camel(verb)}Request"
    schema = create_model(  # type: ignore[call-arg]
        name,
        **{pk_name: (pk_type, Field(...))},  # type: ignore[name-defined]
    )
    return namely_model(
        schema,
        name=name,
        doc=f"{verb} request schema for {model.__name__}",
    )


def _extract_example(schema: Type[BaseModel]) -> Dict[str, Any]:
    """Build a simple example object from field examples if available."""
    try:
        js = schema.model_json_schema()
    except Exception:
        return {}
    out: Dict[str, Any] = {}
    for name, prop in (js.get("properties") or {}).items():
        examples = prop.get("examples")
        if examples:
            out[name] = examples[0]
    return out


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


# ───────────────────────────────────────────────────────────────────────────────
# Core builder (defaults only; overrides are applied later)
# ───────────────────────────────────────────────────────────────────────────────


def _default_schemas_for_spec(
    model: type, sp: OpSpec
) -> Dict[str, Optional[Type[BaseModel]]]:
    """
    Decide default IN/OUT schemas for a given OpSpec (ignores sp.request_model/response_model).

    New rules:
      • Canonical targets → provide canonical defaults.
      • Custom target     → no defaults (raw) unless explicitly overridden.
    """
    target = sp.target
    result: Dict[str, Optional[Type[BaseModel]]] = {
        "in_": None,
        "out": None,
        "in_item": None,
        "out_item": None,
    }

    # Element schema for many OUT shapes
    read_schema: Optional[Type[BaseModel]] = _build_schema(model, verb="read")

    # Canonical targets
    if target == "create":
        item_in = _build_schema(model, verb="create")
        result["in_"] = item_in
        result["out"] = read_schema

    elif target == "read":
        pk_name, pk_type = _pk_info(model)
        result["in_"] = _make_pk_model(model, "read", pk_name, pk_type)
        result["out"] = read_schema

    elif target == "update":
        pk_name, _ = _pk_info(model)
        result["in_"] = _build_schema(model, verb="update", exclude={pk_name})
        result["out"] = read_schema

    elif target == "replace":
        pk_name, _ = _pk_info(model)
        result["in_"] = _build_schema(model, verb="replace", exclude={pk_name})
        result["out"] = read_schema

    elif target == "upsert":
        item_in = _build_schema(model, verb="upsert") or _build_schema(
            model, verb="replace"
        )
        result["in_"] = item_in
        result["out"] = read_schema

    elif target == "delete":
        # For RPC delete, a body with PK is allowed; REST delete ignores body.
        result["in_"] = _build_schema(model, verb="delete")
        result["out"] = read_schema

    elif target == "list":
        params = _build_list_params(model)
        result["in_"] = params
        result["out"] = read_schema

    elif target == "clear":
        params = _build_list_params(model)
        result["in_"] = params
        result["out"] = _make_deleted_response_model(model, "clear")

    elif target == "upsert":
        item_in = _build_schema(model, verb="upsert") or _build_schema(
            model, verb="replace"
        )
        result["in_"] = item_in
        result["out"] = read_schema

    elif target == "bulk_create":
        item_in = _build_schema(model, verb="create")
        result["in_"] = _make_bulk_rows_model(model, "bulk_create", item_in)
        result["in_item"] = item_in
        result["out"] = (
            _make_bulk_rows_response_model(model, "bulk_create", read_schema)
            if read_schema
            else None
        )
        result["out_item"] = read_schema

    elif target == "bulk_update":
        item_in = _build_schema(model, verb="update")
        result["in_"] = _make_bulk_rows_model(model, "bulk_update", item_in)
        result["in_item"] = item_in
        result["out"] = (
            _make_bulk_rows_response_model(model, "bulk_update", read_schema)
            if read_schema
            else None
        )
        result["out_item"] = read_schema

    elif target == "bulk_replace":
        item_in = _build_schema(model, verb="replace")
        result["in_"] = _make_bulk_rows_model(model, "bulk_replace", item_in)
        result["in_item"] = item_in
        result["out"] = (
            _make_bulk_rows_response_model(model, "bulk_replace", read_schema)
            if read_schema
            else None
        )
        result["out_item"] = read_schema

    elif target == "bulk_upsert":
        # Prefer a dedicated 'upsert' item shape if available; otherwise fall back to 'replace'
        item_in = _build_schema(model, verb="upsert") or _build_schema(
            model, verb="replace"
        )
        result["in_"] = _make_bulk_rows_model(model, "bulk_upsert", item_in)
        result["in_item"] = item_in
        result["out"] = (
            _make_bulk_rows_response_model(model, "bulk_upsert", read_schema)
            if read_schema
            else None
        )
        result["out_item"] = read_schema

    elif target == "bulk_delete":
        pk_name, pk_type = _pk_info(model)
        result["in_"] = _make_bulk_ids_model(model, "bulk_delete", pk_type)
        result["out"] = _make_deleted_response_model(model, "bulk_delete")

    elif target == "custom":
        # Build schemas for custom operations based on verb-specific IO specs
        alias = sp.alias
        specs = getattr(model, "__autoapi_cols__", {})
        in_fields = {
            name
            for name, spec in specs.items()
            if alias in set(getattr(getattr(spec, "io", None), "in_verbs", []) or [])
        }
        out_fields = {
            name
            for name, spec in specs.items()
            if alias in set(getattr(getattr(spec, "io", None), "out_verbs", []) or [])
        }
        result["in_"] = (
            _build_schema(model, verb=alias, include=in_fields) if in_fields else None
        )
        result["out"] = (
            _build_schema(model, verb=alias, include=out_fields) if out_fields else None
        )

    else:
        # Defensive default: treat unknown like custom (raw)
        result["in_"] = None
        result["out"] = None

    return result


# ───────────────────────────────────────────────────────────────────────────────
# Public API
# ───────────────────────────────────────────────────────────────────────────────


def build_and_attach(
    model: type, specs: Sequence[OpSpec], *, only_keys: Optional[Sequence[_Key]] = None
) -> None:
    """
    Build request and response schemas per OpSpec and attach them under:
        model.schemas.<alias>.in_   -> request model (or None)
        model.schemas.<alias>.out   -> response model (or None)

    Two-pass strategy:
      0) Seed namespaces from @schema_ctx declarations (so SchemaRef targets exist)
      1) Attach DEFAULT schemas for canonical ops (custom stays raw)
      2) Apply per-spec overrides (SchemaRef / 'alias.in'|'alias.out' / 'raw' / None)

    If `only_keys` is provided, overrides are limited to those (alias,target) pairs.
    Defaults are still ensured for all specs so cross-op SchemaRefs resolve reliably
    for canonical ops.
    """
    if not hasattr(model, "schemas"):
        model.schemas = SimpleNamespace()

    wanted = set(only_keys or ())

    # Pass 0: attach schemas declared via @schema_ctx
    declared = collect_decorated_schemas(model)  # {alias: {"in": cls, "out": cls}}
    for alias, kinds in (declared or {}).items():
        ns = _ensure_alias_namespace(model, alias)
        if "in" in kinds:
            setattr(ns, "in_", kinds["in"])
        if "out" in kinds:
            setattr(ns, "out", kinds["out"])

    # Ensure a namespace per op alias (even if empty)
    for sp in specs:
        _ = _ensure_alias_namespace(model, sp.alias)

    # Pass 1: attach defaults for all specs.
    # Existing schemas that lack fields are treated as missing so they are
    # replaced with freshly built defaults.  This protects against earlier
    # auto-binding passes that may have produced placeholder models.
    for sp in specs:
        ns = _ensure_alias_namespace(model, sp.alias)
        shapes = _default_schemas_for_spec(model, sp)

        if shapes.get("in_") is not None:
            existing_in = getattr(ns, "in_", None)
            if existing_in is None or not getattr(existing_in, "model_fields", None):
                setattr(ns, "in_", shapes["in_"])

        if shapes.get("in_item") is not None:
            existing_in_item = getattr(ns, "in_item", None)
            if existing_in_item is None or not getattr(
                existing_in_item, "model_fields", None
            ):
                setattr(ns, "in_item", shapes["in_item"])

        if shapes.get("out") is not None:
            existing_out = getattr(ns, "out", None)
            if existing_out is None or not getattr(existing_out, "model_fields", None):
                setattr(ns, "out", shapes["out"])

        if shapes.get("out_item") is not None:
            existing_out_item = getattr(ns, "out_item", None)
            if existing_out_item is None or not getattr(
                existing_out_item, "model_fields", None
            ):
                setattr(ns, "out_item", shapes["out_item"])

        logger.debug(
            "schemas(default): %s.%s -> in=%s out=%s",
            model.__name__,
            sp.alias,
            getattr(ns, "in_", None).__name__ if getattr(ns, "in_", None) else None,
            getattr(ns, "out", None).__name__ if getattr(ns, "out", None) else None,
        )

    # Pass 2: apply per-spec overrides (respect only_keys if provided)
    for sp in specs:
        key = (sp.alias, sp.target)
        if wanted and key not in wanted:
            continue

        ns = _ensure_alias_namespace(model, sp.alias)

        if sp.request_model is not None:
            try:
                resolved_in = _resolve_schema_arg(
                    model, sp.request_model
                )  # Optional[Type[BaseModel]]
            except Exception as e:
                logger.exception(
                    "Failed resolving request schema for %s.%s: %s",
                    model.__name__,
                    sp.alias,
                    e,
                )
                raise
            # Set to model or None (raw)
            setattr(ns, "in_", resolved_in)

        if sp.response_model is not None:
            try:
                resolved_out = _resolve_schema_arg(
                    model, sp.response_model
                )  # Optional[Type[BaseModel]]
            except Exception as e:
                logger.exception(
                    "Failed resolving response schema for %s.%s: %s",
                    model.__name__,
                    sp.alias,
                    e,
                )
                raise
            # Set to model or None (raw)
            setattr(ns, "out", resolved_out)

        logger.debug(
            "schemas(override): %s.%s -> in=%s out=%s",
            model.__name__,
            sp.alias,
            getattr(ns, "in_", None).__name__ if getattr(ns, "in_", None) else None,
            getattr(ns, "out", None).__name__ if getattr(ns, "out", None) else None,
        )


__all__ = ["build_and_attach"]
