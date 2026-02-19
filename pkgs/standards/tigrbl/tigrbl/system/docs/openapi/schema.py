"""OpenAPI document builder for stdapi routers."""

from __future__ import annotations

from typing import Any

from ....runtime.status.mappings import status
from .helpers import (
    _request_schema_from_handler,
    _resolve_component_schema_ref,
    _schema_from_model,
    _security_from_dependencies,
    _security_schemes_from_dependencies,
)


def openapi(router: Any) -> dict[str, Any]:
    paths: dict[str, Any] = {}
    components: dict[str, Any] = {"schemas": {}}
    components_schemas: dict[str, Any] = components["schemas"]

    for route in getattr(router, "_routes", []):
        if not route.include_in_schema:
            continue

        canonical_path = route.path_template.rstrip("/") or "/"
        if canonical_path == "/openrpc.json" or route.name == "openrpc_json":
            continue

        path_item = paths.setdefault(canonical_path, {})
        for method in sorted(route.methods):
            status_code = route.status_code or status.HTTP_200_OK
            responses: dict[str, Any] = {}
            if route.responses:
                for code, meta in route.responses.items():
                    entry: dict[str, Any] = {
                        "description": meta.get("description", "") or "",
                    }
                    model = meta.get("model")
                    if model is not None:
                        entry["content"] = {
                            "application/json": {
                                "schema": _schema_from_model(
                                    model,
                                    components_schemas,
                                )
                            }
                        }
                    responses[str(code)] = entry
            if str(status_code) not in responses:
                entry = {"description": "Successful Response"}
                schema = route.response_schema
                if schema is None and route.response_model is not None:
                    schema = _schema_from_model(
                        route.response_model,
                        components_schemas,
                    )
                if schema is not None:
                    entry["content"] = {"application/json": {"schema": schema}}
                responses[str(status_code)] = entry

            op: dict[str, Any] = {
                "operationId": route.operation_id or route.name,
                "responses": responses,
            }
            if route.summary:
                op["summary"] = route.summary
            if route.description:
                op["description"] = route.description
            if route.tags:
                op["tags"] = route.tags
            if route.deprecated:
                op["deprecated"] = True

            params: list[dict[str, Any]] = []
            for param_name in route.param_names:
                schema = (route.path_param_schemas or {}).get(param_name) or {
                    "type": "string"
                }
                params.append(
                    {
                        "name": param_name,
                        "in": "path",
                        "required": True,
                        "schema": schema,
                    }
                )

            for qname, qschema in (route.query_param_schemas or {}).items():
                params.append(
                    {
                        "name": qname,
                        "in": "query",
                        "required": bool(qschema.get("required", False)),
                        "schema": {k: v for k, v in qschema.items() if k != "required"},
                    }
                )

            if params:
                op["parameters"] = params

            request_schema = route.request_schema
            if request_schema is None and route.request_model is not None:
                request_schema = _schema_from_model(
                    route.request_model,
                    components_schemas,
                )

            alias = route.name.rsplit(".", maxsplit=1)[-1]
            if request_schema is None:
                request_schema = _request_schema_from_handler(route, components_schemas)

            if isinstance(request_schema, dict) and alias.startswith("bulk_"):
                request_schema = _resolve_component_schema_ref(
                    request_schema,
                    components_schemas,
                )

            if request_schema is not None:
                op["requestBody"] = {
                    "required": True,
                    "content": {"application/json": {"schema": request_schema}},
                }

            security_deps = list(route.dependencies or []) + list(
                getattr(route, "security_dependencies", None) or []
            )
            sec = _security_from_dependencies(security_deps)
            if sec:
                op["security"] = sec
                components.setdefault("securitySchemes", {}).update(
                    _security_schemes_from_dependencies(security_deps)
                )

            path_item[method.lower()] = op

    doc: dict[str, Any] = {
        "openapi": "3.1.0",
        "info": {"title": router.title, "version": router.version},
        "paths": paths,
        "components": components,
    }
    if router.description:
        doc["info"]["description"] = router.description
    return doc
