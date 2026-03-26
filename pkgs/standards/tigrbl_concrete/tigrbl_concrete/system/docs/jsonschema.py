from __future__ import annotations

from pprint import pformat
from typing import Any, Dict

from pydantic import BaseModel

from tigrbl_concrete._concrete._response import Response
from tigrbl_concrete.system.docs.runtime_ops import register_runtime_get_route

from .openrpc import _iter_models

JsonObject = Dict[str, Any]


def _with_leading_slash(path: str) -> str:
    return path if path.startswith("/") else f"/{path}"


def _model_schema(model: type) -> JsonObject:
    if issubclass(model, BaseModel):
        return model.model_json_schema()
    return {"title": model.__name__, "type": "object"}


def build_json_schema_spec(router: Any) -> JsonObject:
    schemas: JsonObject = {}
    for model in _iter_models(router):
        schemas[model.__name__] = _model_schema(model)

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": getattr(router, "title", None)
        or getattr(router, "name", None)
        or "API",
        "type": "object",
        "properties": schemas,
        "additionalProperties": False,
    }


def mount_json_schema(
    router: Any,
    *,
    path: str = "/json-schema.json",
    name: str = "json_schema",
) -> Any:
    """Mount a JSON Schema-styled documentation endpoint onto ``router``."""

    normalized_path = _with_leading_slash(path)
    setattr(router, "json_schema_path", normalized_path)

    def _json_schema_handler(_request: Any) -> Response:
        spec = build_json_schema_spec(router)
        return Response.text(pformat(spec, indent=4, width=1, sort_dicts=False))

    register_runtime_get_route(
        router,
        path=normalized_path,
        alias=name,
        endpoint=_json_schema_handler,
    )

    router.add_route(
        normalized_path,
        _json_schema_handler,
        methods=["GET"],
        name=name,
        include_in_schema=False,
    )
    return router


__all__ = ["build_json_schema_spec", "mount_json_schema"]
