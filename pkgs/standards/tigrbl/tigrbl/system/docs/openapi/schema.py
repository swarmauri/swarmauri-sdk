"""OpenAPI document builder for std routers."""

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
            alias = (
                getattr(route, "tigrbl_alias", None)
                or route.name.rsplit(".", maxsplit=1)[-1]
            )
            status_code = route.status_code or (
                status.HTTP_201_CREATED if alias == "create" else status.HTTP_200_OK
            )
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

            if request_schema is None:
                request_schema = _request_schema_from_handler(route, components_schemas)

            if isinstance(request_schema, dict) and alias.startswith("bulk_"):
                request_schema = _bulk_schema(
                    request_schema,
                    components_schemas,
                )

            if alias.startswith("bulk_"):
                for response_entry in responses.values():
                    content = response_entry.get("content")
                    if not isinstance(content, dict):
                        continue
                    app_json = content.get("application/json")
                    if not isinstance(app_json, dict):
                        continue
                    schema = app_json.get("schema")
                    if not isinstance(schema, dict):
                        continue
                    app_json["schema"] = _bulk_schema(schema, components_schemas)

            if request_schema is not None:
                op["requestBody"] = {
                    "required": True,
                    "content": {"application/json": {"schema": request_schema}},
                }

            model = getattr(route, "tigrbl_model", None)
            alias = getattr(route, "tigrbl_alias", None)
            security_deps: list[Any] = []
            security_deps.extend(list(getattr(router, "dependencies", None) or ()))
            security_deps.extend(list(getattr(route, "dependencies", None) or ()))
            security_deps.extend(
                list(getattr(route, "security_dependencies", None) or ())
            )
            if model is not None and isinstance(alias, str):
                specs = getattr(getattr(model, "ops", None), "by_alias", {})
                sp_list = specs.get(alias) or ()
                if sp_list:
                    security_deps.extend(list(getattr(sp_list[0], "secdeps", ()) or ()))

            for dep in tuple(getattr(route, "dependencies", ()) or ()):
                if dep not in security_deps:
                    security_deps.append(dep)

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


def _bulk_schema(
    schema: dict[str, Any],
    components_schemas: dict[str, Any],
) -> dict[str, Any]:
    item_schema = _resolve_component_schema_ref(schema, components_schemas)
    wrapped: dict[str, Any] = {"type": "array", "items": item_schema}
    if isinstance(item_schema, dict):
        example = _object_example(item_schema)
        if example:
            wrapped["examples"] = [[example]]
    return wrapped


def _object_example(schema: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    properties = schema.get("properties")
    if not isinstance(properties, dict):
        return out
    for name, prop in properties.items():
        if not isinstance(prop, dict):
            continue
        examples = prop.get("examples")
        if isinstance(examples, list) and examples:
            out[name] = examples[0]
            continue
        if "default" in prop and prop["default"] is not None:
            out[name] = prop["default"]
    return out
