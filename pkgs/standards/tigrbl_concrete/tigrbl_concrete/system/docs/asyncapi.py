from __future__ import annotations

from pprint import pformat
from typing import Any, Dict

from tigrbl_concrete._concrete._response import Response
from tigrbl_concrete.system.docs.runtime_ops import register_runtime_get_route

from .openrpc import (
    _iter_models,
    _iter_ops,
    _is_docs_only_op,
    _schema_with_defs,
)

JsonObject = Dict[str, Any]


def _with_leading_slash(path: str) -> str:
    return path if path.startswith("/") else f"/{path}"


def build_asyncapi_spec(router: Any) -> JsonObject:
    info_title = (
        getattr(router, "title", None) or getattr(router, "name", None) or "API"
    )
    info_version = getattr(router, "version", None) or "0.1.0"
    spec: JsonObject = {
        "asyncapi": "3.0.0",
        "info": {"title": f"{info_title} AsyncAPI", "version": info_version},
        "channels": {},
        "operations": {},
        "components": {"schemas": {}},
    }

    channels = spec["channels"]
    operations = spec["operations"]
    components = spec["components"]["schemas"]

    for model in _iter_models(router):
        model_key = model.__name__
        for op in _iter_ops(model):
            if not getattr(op, "expose_rpc", True):
                continue
            if _is_docs_only_op(op):
                continue

            op_name = f"{model_key}.{op.alias}"
            channel_name = f"{model_key}/{op.alias}"

            alias_ns = getattr(getattr(model, "schemas", None), op.alias, None)
            in_schema = getattr(alias_ns, "in_", None)
            out_schema = getattr(alias_ns, "out", None)

            request_message: JsonObject | None = None
            if in_schema is not None:
                in_json, defs = _schema_with_defs(in_schema)
                components.update(defs)
                request_message = {"payload": in_json}

            reply_message: JsonObject | None = None
            if out_schema is not None:
                out_json, defs = _schema_with_defs(out_schema)
                components.update(defs)
                reply_message = {"payload": out_json}

            channels[channel_name] = {"address": channel_name, "messages": {}}
            if request_message is not None:
                channels[channel_name]["messages"]["request"] = request_message
            if reply_message is not None:
                channels[channel_name]["messages"]["reply"] = reply_message

            operations[op_name] = {
                "action": "send",
                "channel": {"$ref": f"#/channels/{channel_name}"},
                "messages": [{"$ref": f"#/channels/{channel_name}/messages/request"}],
            }

            if reply_message is not None:
                operations[op_name]["reply"] = {
                    "messages": [{"$ref": f"#/channels/{channel_name}/messages/reply"}]
                }

    return spec


def mount_asyncapi(
    router: Any,
    *,
    path: str = "/asyncapi.json",
    name: str = "asyncapi_json",
) -> Any:
    """Mount an AsyncAPI-styled documentation endpoint onto ``router``."""

    normalized_path = _with_leading_slash(path)
    setattr(router, "asyncapi_path", normalized_path)

    def _asyncapi_handler(_request: Any) -> Response:
        spec = build_asyncapi_spec(router)
        return Response.text(pformat(spec, indent=4, width=1, sort_dicts=False))

    register_runtime_get_route(
        router,
        path=normalized_path,
        alias=name,
        endpoint=_asyncapi_handler,
    )

    router.add_route(
        normalized_path,
        _asyncapi_handler,
        methods=["GET"],
        name=name,
        include_in_schema=False,
    )
    return router


__all__ = ["build_asyncapi_spec", "mount_asyncapi"]
