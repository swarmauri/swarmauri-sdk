from __future__ import annotations

import logging
from typing import Any, Dict, List, Type

from pydantic import BaseModel, ConfigDict, Field, RootModel, create_model

logger = logging.getLogger("uvicorn")


def namely_model(model: Type[BaseModel], *, name: str, doc: str) -> Type[BaseModel]:
    """Assign a unique name and docstring to a Pydantic model class."""
    logger.debug("Renaming model %s to %s", model.__name__, name)
    model.__name__ = name
    model.__qualname__ = name
    model.__doc__ = doc

    # Rebuild the model so Pydantic updates internal references (e.g., for OpenAPI titles).

    model.model_rebuild(force=True)
    logger.debug("Model %s rebuilt", name)
    return model


def _camel(s: str) -> str:
    rv = "".join(p.capitalize() or "_" for p in s.split("_"))
    logger.debug("Camel-cased '%s' → '%s'", s, rv)
    return rv


def _extract_example(schema: Type[BaseModel]) -> Dict[str, Any]:
    """Build a simple example object from field examples if available."""
    try:
        js = schema.model_json_schema()
    except Exception as exc:
        logger.debug("Failed to build JSON schema for %s: %s", schema, exc)
        return {}
    out: Dict[str, Any] = {}
    for name, prop in (js.get("properties") or {}).items():
        examples = prop.get("examples")
        if examples:
            out[name] = examples[0]
    logger.debug("Extracted example for %s: %s", schema, out)
    return out


def _make_bulk_rows_model(
    model: type, verb: str, item_schema: Type[BaseModel]
) -> Type[BaseModel]:
    """Build a root model representing ``List[item_schema]``."""
    name = f"{model.__name__}{_camel(verb)}Request"
    example = _extract_example(item_schema)
    examples = [[example]] if example else []

    class _BulkModel(RootModel[List[item_schema]]):  # type: ignore[misc]
        model_config = ConfigDict(json_schema_extra={"examples": examples})

    logger.debug("Built bulk rows model %s with examples=%s", name, examples)
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

    class _BulkModel(RootModel[List[item_schema]]):  # type: ignore[misc]
        model_config = ConfigDict(json_schema_extra={"examples": examples})

    logger.debug("Built bulk rows response model %s with examples=%s", name, examples)
    return namely_model(
        _BulkModel,
        name=name,
        doc=f"{verb} response schema for {model.__name__}",
    )


def _make_bulk_ids_model(
    model: type, verb: str, pk_type: type | Any
) -> Type[BaseModel]:
    """Build a wrapper schema with an ``ids: List[pk_type]`` field."""
    name = f"{model.__name__}{_camel(verb)}Request"
    schema = create_model(  # type: ignore[call-arg]
        name,
        ids=(List[pk_type], Field(...)),  # type: ignore[name-defined]
    )
    logger.debug("Built bulk ids model %s", name)
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
    logger.debug("Built deleted response model %s", name)
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
    logger.debug("Built pk model %s for field %s", name, pk_name)
    return namely_model(
        schema,
        name=name,
        doc=f"{verb} request schema for {model.__name__}",
    )


__all__ = [
    "namely_model",
    "_make_bulk_rows_model",
    "_make_bulk_rows_response_model",
    "_make_bulk_ids_model",
    "_make_deleted_response_model",
    "_make_pk_model",
]
