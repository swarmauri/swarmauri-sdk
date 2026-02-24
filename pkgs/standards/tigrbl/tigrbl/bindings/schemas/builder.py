from __future__ import annotations

# tigrbl/v3/bindings/schemas/builder.py

import logging
from types import SimpleNamespace
from typing import Dict, Optional, Sequence, Type

from pydantic import BaseModel

from ...op import OpSpec
from ...schema import collect_decorated_schemas
from .defaults import _default_schemas_for_spec
from .utils import _alias_schema, _ensure_alias_namespace, _resolve_schema_arg, _Key

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/schemas/builder")


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
    logger.debug(
        "Building schemas for %s with %d specs (only_keys=%s)",
        model.__name__,
        len(specs),
        only_keys,
    )
    if not hasattr(model, "schemas"):
        model.schemas = SimpleNamespace()
        logger.debug("Created new schemas namespace on %s", model.__name__)
    else:
        logger.debug("Using existing schemas namespace on %s", model.__name__)

    wanted = set(only_keys or ())
    if wanted:
        logger.debug("Filtering overrides to keys: %s", wanted)

    # Pass 0: attach schemas declared via @schema_ctx
    declared = collect_decorated_schemas(model)  # {alias: {"in": cls, "out": cls}}
    for alias, kinds in (declared or {}).items():
        logger.debug("Applying declared schemas for alias '%s'", alias)
        ns = _ensure_alias_namespace(model, alias)
        if "in" in kinds:
            setattr(ns, "in_", kinds["in"])
            logger.debug("Declared request schema for %s.%s", model.__name__, alias)
        if "out" in kinds:
            setattr(ns, "out", kinds["out"])
            logger.debug("Declared response schema for %s.%s", model.__name__, alias)

    # Ensure a namespace per op alias (even if empty)
    for sp in specs:
        _ = _ensure_alias_namespace(model, sp.alias)
        logger.debug("Ensured namespace for alias '%s'", sp.alias)

    # Pass 1: attach defaults for all specs and capture them so canonical
    # defaults can be restored later if needed.
    # Existing schemas that lack fields are treated as missing so they are
    # replaced with freshly built defaults.  This protects against earlier
    # auto-binding passes that may have produced placeholder models.
    defaults: Dict[_Key, Dict[str, Optional[Type[BaseModel]]]] = {}
    for sp in specs:
        ns = _ensure_alias_namespace(model, sp.alias)
        shapes = _default_schemas_for_spec(model, sp)
        defaults[(sp.alias, sp.target)] = shapes

        if shapes.get("in_") is not None:
            existing_in = getattr(ns, "in_", None)
            if existing_in is None or not getattr(existing_in, "model_fields", None):
                setattr(ns, "in_", shapes["in_"])
                logger.debug(
                    "Attached default request schema for %s.%s",
                    model.__name__,
                    sp.alias,
                )
            else:
                logger.debug(
                    "Keeping existing request schema for %s.%s",
                    model.__name__,
                    sp.alias,
                )
        else:
            logger.debug(
                "No default request schema for %s.%s", model.__name__, sp.alias
            )

        if shapes.get("in_item") is not None:
            existing_in_item = getattr(ns, "in_item", None)
            if existing_in_item is None or not getattr(
                existing_in_item, "model_fields", None
            ):
                setattr(ns, "in_item", shapes["in_item"])
                logger.debug(
                    "Attached default request item schema for %s.%s",
                    model.__name__,
                    sp.alias,
                )
            else:
                logger.debug(
                    "Keeping existing request item schema for %s.%s",
                    model.__name__,
                    sp.alias,
                )
        else:
            logger.debug(
                "No default request item schema for %s.%s", model.__name__, sp.alias
            )

        if shapes.get("out") is not None:
            existing_out = getattr(ns, "out", None)
            if existing_out is None or not getattr(existing_out, "model_fields", None):
                setattr(ns, "out", shapes["out"])
                logger.debug(
                    "Attached default response schema for %s.%s",
                    model.__name__,
                    sp.alias,
                )
            else:
                logger.debug(
                    "Keeping existing response schema for %s.%s",
                    model.__name__,
                    sp.alias,
                )
        else:
            logger.debug(
                "No default response schema for %s.%s", model.__name__, sp.alias
            )

        if shapes.get("out_item") is not None:
            existing_out_item = getattr(ns, "out_item", None)
            if existing_out_item is None or not getattr(
                existing_out_item, "model_fields", None
            ):
                setattr(ns, "out_item", shapes["out_item"])
                logger.debug(
                    "Attached default response item schema for %s.%s",
                    model.__name__,
                    sp.alias,
                )
            else:
                logger.debug(
                    "Keeping existing response item schema for %s.%s",
                    model.__name__,
                    sp.alias,
                )
        else:
            logger.debug(
                "No default response item schema for %s.%s", model.__name__, sp.alias
            )

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
            logger.debug(
                "Skipping overrides for %s.%s not in only_keys",
                model.__name__,
                sp.alias,
            )
            continue

        ns = _ensure_alias_namespace(model, sp.alias)

        if sp.request_model is not None:
            logger.debug(
                "Resolving request override for %s.%s", model.__name__, sp.alias
            )
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
            setattr(ns, "in_", resolved_in)
            logger.debug(
                "Request override for %s.%s resolved to %s",
                model.__name__,
                sp.alias,
                getattr(resolved_in, "__name__", None),
            )
        else:
            logger.debug("No request override for %s.%s", model.__name__, sp.alias)

        if sp.response_model is not None:
            logger.debug(
                "Resolving response override for %s.%s", model.__name__, sp.alias
            )
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
            setattr(ns, "out", resolved_out)
            logger.debug(
                "Response override for %s.%s resolved to %s",
                model.__name__,
                sp.alias,
                getattr(resolved_out, "__name__", None),
            )
        else:
            logger.debug("No response override for %s.%s", model.__name__, sp.alias)

        logger.debug(
            "schemas(override): %s.%s -> in=%s out=%s",
            model.__name__,
            sp.alias,
            getattr(ns, "in_", None).__name__ if getattr(ns, "in_", None) else None,
            getattr(ns, "out", None).__name__ if getattr(ns, "out", None) else None,
        )

    # Pass 2b: restore canonical defaults if overrides cleared them
    for sp in specs:
        if sp.target == "custom":
            logger.debug(
                "Skipping default restoration for custom target %s.%s",
                model.__name__,
                sp.alias,
            )
            continue
        ns = _ensure_alias_namespace(model, sp.alias)
        shapes = defaults.get((sp.alias, sp.target)) or {}
        if getattr(ns, "in_", None) is None and shapes.get("in_") is not None:
            setattr(ns, "in_", shapes["in_"])
            logger.debug(
                "Restored default request schema for %s.%s", model.__name__, sp.alias
            )
        else:
            logger.debug(
                "No request schema restoration needed for %s.%s",
                model.__name__,
                sp.alias,
            )
        if getattr(ns, "in_item", None) is None and shapes.get("in_item") is not None:
            setattr(ns, "in_item", shapes["in_item"])
            logger.debug(
                "Restored default request item schema for %s.%s",
                model.__name__,
                sp.alias,
            )
        else:
            logger.debug(
                "No request item schema restoration needed for %s.%s",
                model.__name__,
                sp.alias,
            )
        if getattr(ns, "out", None) is None and shapes.get("out") is not None:
            setattr(ns, "out", shapes["out"])
            logger.debug(
                "Restored default response schema for %s.%s", model.__name__, sp.alias
            )
        else:
            logger.debug(
                "No response schema restoration needed for %s.%s",
                model.__name__,
                sp.alias,
            )
        if getattr(ns, "out_item", None) is None and shapes.get("out_item") is not None:
            setattr(ns, "out_item", shapes["out_item"])
            logger.debug(
                "Restored default response item schema for %s.%s",
                model.__name__,
                sp.alias,
            )
        else:
            logger.debug(
                "No response item schema restoration needed for %s.%s",
                model.__name__,
                sp.alias,
            )

    # Pass 3: ensure alias-specific request/response schema names
    for sp in specs:
        ns = _ensure_alias_namespace(model, sp.alias)
        in_model = getattr(ns, "in_", None)
        if (
            isinstance(in_model, type)
            and issubclass(in_model, BaseModel)
            and getattr(in_model, "__tigrbl_schema_decl__", None) is None
        ):
            logger.debug("Aliasing request schema for %s.%s", model.__name__, sp.alias)
            setattr(
                ns,
                "in_",
                _alias_schema(in_model, model=model, alias=sp.alias, kind="Request"),
            )
        else:
            logger.debug(
                "Request schema for %s.%s already aliased or missing",
                model.__name__,
                sp.alias,
            )
        out_model = getattr(ns, "out", None)
        if (
            isinstance(out_model, type)
            and issubclass(out_model, BaseModel)
            and getattr(out_model, "__tigrbl_schema_decl__", None) is None
        ):
            logger.debug("Aliasing response schema for %s.%s", model.__name__, sp.alias)
            setattr(
                ns,
                "out",
                _alias_schema(out_model, model=model, alias=sp.alias, kind="Response"),
            )
        else:
            logger.debug(
                "Response schema for %s.%s already aliased or missing",
                model.__name__,
                sp.alias,
            )


__all__ = ["build_and_attach"]
