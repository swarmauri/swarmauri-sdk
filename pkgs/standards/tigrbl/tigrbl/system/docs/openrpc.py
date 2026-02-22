from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Sequence

from pydantic import BaseModel

from ...responses import Response
from ...op import OpSpec
from .openapi.helpers import (
    _security_from_dependencies,
    _security_schemes_from_dependencies,
)

JsonObject = Dict[str, Any]


def _with_leading_slash(path: str) -> str:
    return path if path.startswith("/") else f"/{path}"


def _jsonrpc_path(router: Any) -> str:
    configured = getattr(router, "jsonrpc_prefix", None) or "/rpc"
    return _with_leading_slash(str(configured)).rstrip("/") or "/"


def _request_origin(request: Any) -> str | None:
    headers = getattr(request, "headers", None)
    if headers is None or not hasattr(headers, "get"):
        return None

    forwarded_host = headers.get("x-forwarded-host")
    host = forwarded_host or headers.get("host")
    if not host:
        return None
    host = str(host).split(",", maxsplit=1)[0].strip()
    if not host:
        return None

    proto = (
        headers.get("x-forwarded-proto")
        or headers.get("x-forwarded-protocol")
        or headers.get("x-forwarded-scheme")
    )
    forwarded = headers.get("forwarded", "")
    if not (forwarded_host or proto or forwarded):
        return None

    scheme = None
    if proto:
        scheme = str(proto).split(",", maxsplit=1)[0].strip()

    if not scheme:
        request_url = getattr(request, "url", None)
        if request_url is not None:
            scheme = getattr(request_url, "scheme", None)

    if not scheme:
        scope = getattr(request, "scope", None)
        if isinstance(scope, Mapping):
            scheme = scope.get("scheme")

    if not scheme:
        scheme = "https" if str(forwarded).lower().find("proto=https") >= 0 else "http"
    return f"{scheme}://{host}"


def _iter_models(router: Any) -> List[type]:
    seen: set[type] = set()
    models: List[type] = []

    def _add_from(container: Any) -> None:
        if isinstance(container, Mapping):
            items: Iterable[Any] = container.values()
        elif isinstance(container, Sequence):
            items = container
        else:
            return
        for model in items:
            if isinstance(model, type) and model not in seen:
                seen.add(model)
                models.append(model)

    _add_from(getattr(router, "models", None) or {})
    for child in getattr(router, "apis", ()) or ():
        _add_from(getattr(child, "models", None) or {})

    return models


def _iter_ops(model: type) -> Sequence[OpSpec]:
    ops = getattr(model, "ops", None)
    if ops is not None:
        all_ops = getattr(ops, "all", None)
        if all_ops is not None:
            return all_ops
    opspecs = getattr(model, "opspecs", None)
    if opspecs is not None:
        all_ops = getattr(opspecs, "all", None)
        if all_ops is not None:
            return all_ops
    return ()


def _schema_with_defs(schema: type[BaseModel]) -> tuple[JsonObject, JsonObject]:
    raw = schema.model_json_schema(ref_template="#/components/schemas/{model}")
    defs = raw.pop("$defs", {})
    return raw, defs


def _describe_method(model: type, spec: OpSpec) -> str | None:
    rpc_ns = getattr(model, "rpc", None)
    rpc_call = getattr(rpc_ns, spec.alias, None)
    if rpc_call is None:
        return None
    doc = getattr(rpc_call, "__doc__", None)
    if doc:
        return doc.strip()
    return None


def build_openrpc_spec(router: Any, request: Any | None = None) -> JsonObject:
    info_title = (
        getattr(router, "title", None) or getattr(router, "name", None) or "API"
    )
    info_version = getattr(router, "version", None) or "0.1.0"
    jsonrpc_url = _jsonrpc_path(router)
    origin = _request_origin(request)
    server_url = f"{origin}{jsonrpc_url}" if origin else jsonrpc_url
    spec: JsonObject = {
        "openrpc": "1.2.6",
        "info": {"title": f"{info_title} JSON-RPC API", "version": info_version},
        "servers": [{"name": info_title, "url": server_url}],
        "methods": [],
        "components": {"schemas": {}, "securitySchemes": {}},
    }

    components = spec["components"]["schemas"]
    security_schemes = spec["components"]["securitySchemes"]
    methods: List[JsonObject] = []

    for model in _iter_models(router):
        for op in _iter_ops(model):
            if not getattr(op, "expose_rpc", True):
                continue

            method: JsonObject = {"name": f"{model.__name__}.{op.alias}"}
            description = _describe_method(model, op)
            if description:
                method["description"] = description

            alias_ns = getattr(getattr(model, "schemas", None), op.alias, None)
            in_schema = getattr(alias_ns, "in_", None)
            out_schema = getattr(alias_ns, "out", None)

            if in_schema is not None:
                in_json, defs = _schema_with_defs(in_schema)
                for key, value in defs.items():
                    components.setdefault(key, value)
                method["params"] = [
                    {"name": "params", "schema": in_json, "required": True}
                ]
                method["paramStructure"] = "by-name"
            else:
                method["params"] = []

            if out_schema is not None:
                out_json, defs = _schema_with_defs(out_schema)
                for key, value in defs.items():
                    components.setdefault(key, value)
                method["result"] = {"name": "result", "schema": out_json}

            secdeps = tuple(getattr(op, "secdeps", ()) or ())
            security = _security_from_dependencies(secdeps)
            if security:
                method["security"] = security
                security_schemes.update(_security_schemes_from_dependencies(secdeps))

            methods.append(method)

    spec["methods"] = sorted(methods, key=lambda item: item["name"])
    return spec


def mount_openrpc(
    router: Any,
    app: Any | None = None,
    *,
    path: str = "/openrpc.json",
    name: str = "openrpc_json",
    tags: list[str] | None = None,
) -> Any:
    """Mount an OpenRPC JSON endpoint onto ``app`` or ``router``."""

    target_router = app if app is not None else router
    normalized_path = _with_leading_slash(path)
    setattr(router, "openrpc_path", normalized_path)

    def _openrpc_endpoint(request: Any) -> Response:
        return Response.json(build_openrpc_spec(router, request=request))

    target_router.add_api_route(
        normalized_path,
        _openrpc_endpoint,
        methods=["GET"],
        name=name,
        include_in_schema=False,
        tags=list(tags) if tags else None,
        summary="OpenRPC",
        description="OpenRPC 1.2.6 schema for JSON-RPC methods.",
    )
    return target_router


__all__ = ["build_openrpc_spec", "mount_openrpc"]
