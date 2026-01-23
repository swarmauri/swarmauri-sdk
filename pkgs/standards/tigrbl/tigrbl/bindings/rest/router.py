from __future__ import annotations
import logging

import inspect
import re
from uuid import uuid4
from typing import Any, Sequence

from .collection import _make_collection_endpoint
from .member import _make_member_endpoint
from .common import (
    TIGRBL_ALLOW_ANON_ATTR,
    TIGRBL_AUTH_DEP_ATTR,
    TIGRBL_GET_DB_ATTR,
    TIGRBL_REST_DEPENDENCIES_ATTR,
    BaseModel,
    CANON,
    OpSpec,
    Response,
    Router,
    _DEFAULT_METHODS,
    _default_path_suffix,
    _nested_prefix,
    _normalize_deps,
    _normalize_secdeps,
    _optionalize_list_in_model,
    _path_for_spec,
    _require_auth_header,
    _requires_auth_header,
    _req_state_db,
    _resource_name,
    _status,
    _status_for,
    _strip_parent_fields,
    _RESPONSES_META,
)
from ...schema import _make_bulk_rows_model
import typing as _typing
from typing import get_args as _get_args, get_origin as _get_origin

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/rest/router")


def _build_router(
    model: type, specs: Sequence[OpSpec], *, api: Any | None = None
) -> Router:
    resource = _resource_name(model)

    # Router-level deps: extra deps only (transport-level; never part of kernel plan)
    extra_router_deps = _normalize_deps(
        getattr(model, TIGRBL_REST_DEPENDENCIES_ATTR, None)
    )
    auth_dep = getattr(model, TIGRBL_AUTH_DEP_ATTR, None)

    # Verbs explicitly allowed without auth
    allow_anon_attr = getattr(model, TIGRBL_ALLOW_ANON_ATTR, None)
    allow_anon = set(
        allow_anon_attr() if callable(allow_anon_attr) else allow_anon_attr or []
    )

    router = Router(dependencies=extra_router_deps or None)

    pk_param = "item_id"
    db_dep = getattr(model, TIGRBL_GET_DB_ATTR, None) or _req_state_db

    raw_nested = _nested_prefix(model) or ""
    nested_pref = re.sub(r"/{2,}", "/", raw_nested).rstrip("/") or ""
    nested_vars = re.findall(r"{(\w+)}", raw_nested)

    # When models are mounted on nested paths, parent identifiers should not
    # appear in request schemas.  Capture the original spec sequence so we can
    # prune request models even if some specs (e.g. ``create`` when
    # ``bulk_create`` is present) are later dropped from the router.
    all_specs = list(specs)

    if nested_vars:
        schemas_root = getattr(model, "schemas", None)
        if schemas_root:
            for sp in all_specs:
                alias_ns = getattr(schemas_root, sp.alias, None)
                if not alias_ns:
                    continue
                in_model = getattr(alias_ns, "in_", None)
                if (
                    in_model
                    and inspect.isclass(in_model)
                    and issubclass(in_model, BaseModel)
                ):
                    root_field = getattr(in_model, "model_fields", {}).get("root")
                    if root_field is not None:
                        ann = root_field.annotation
                        inner = None
                        for t in _get_args(ann) or (ann,):
                            origin = _get_origin(t)
                            if origin in {list, _typing.List}:
                                t_args = _get_args(t)
                                if t_args:
                                    t = t_args[0]
                                    origin = _get_origin(t)
                            if inspect.isclass(t) and issubclass(t, BaseModel):
                                inner = t
                                break
                        if inner is not None:
                            pruned = _strip_parent_fields(inner, drop=set(nested_vars))
                            setattr(alias_ns, "in_item", pruned)
                            setattr(
                                alias_ns,
                                "in_",
                                _make_bulk_rows_model(model, sp.target, pruned),
                            )
                            continue
                    pruned = _strip_parent_fields(in_model, drop=set(nested_vars))
                    setattr(alias_ns, "in_", pruned)

    # If bulk_delete is present, drop clear to avoid route conflicts
    if any(sp.target == "bulk_delete" for sp in specs):
        specs = [sp for sp in specs if sp.target != "clear"]

    # When both ``create`` and ``bulk_create`` handlers are available,
    # prefer ``bulk_create`` for the REST route to avoid conflicting POST
    # registrations at the collection path. Both operations remain bound
    # for schema generation, but only ``bulk_create`` should surface as a
    # REST endpoint and in the OpenAPI spec.
    if any(sp.target == "bulk_create" for sp in specs) and any(
        sp.target == "create" for sp in specs
    ):
        specs = [sp for sp in specs if sp.target != "create"]

    # Register collection-level bulk routes before member routes so static paths
    # like "/resource/bulk" aren't captured by dynamic member routes such as
    # "/resource/{item_id}". FastAPI matches routes in the order they are
    # added, so sorting here prevents "bulk" from being treated as an
    # identifier.
    specs = sorted(
        specs,
        key=lambda sp: (
            -1
            if sp.target == "clear"
            else 0
            if sp.target in {"bulk_update", "bulk_replace", "bulk_delete", "bulk_merge"}
            else 1
            if sp.target in {"create", "merge"}
            else 2
            if sp.target in {"bulk_create"}
            else 3
        ),
    )

    for sp in specs:
        if not sp.expose_routes:
            continue

        # Determine path and membership
        if nested_pref:
            if sp.path_suffix is None:
                suffix = _default_path_suffix(sp) or ""
            else:
                suffix = sp.path_suffix or ""
            if suffix and not suffix.startswith("/"):
                suffix = "/" + suffix
            base = nested_pref.rstrip("/")
            if not base.endswith(f"/{resource}"):
                base = f"{base}/{resource}"
            if sp.arity == "member" or sp.target in {
                "read",
                "update",
                "replace",
                "merge",
                "delete",
            }:
                path = f"{base}/{{{pk_param}}}{suffix}"
                is_member = True
            else:
                path = f"{base}{suffix}"
                is_member = False
        else:
            path, is_member = _path_for_spec(
                model, sp, resource=resource, pk_param=pk_param
            )

        # HARDEN list.in_ at runtime to avoid bogus defaults blowing up empty GETs
        if sp.target == "list":
            schemas_root = getattr(model, "schemas", None)
            if schemas_root:
                alias_ns = getattr(schemas_root, sp.alias, None)
                if alias_ns:
                    in_model = getattr(alias_ns, "in_", None)
                    if (
                        in_model
                        and inspect.isclass(in_model)
                        and issubclass(in_model, BaseModel)
                        and not getattr(in_model, "__tigrbl_optionalized__", False)
                    ):
                        safe = _optionalize_list_in_model(in_model)
                        setattr(alias_ns, "in_", safe)

        # HTTP methods
        methods = list(sp.http_methods or _DEFAULT_METHODS.get(sp.target, ("POST",)))
        response_model = None  # Allow hooks to mutate response freely

        # Build endpoint (split by body/no-body)
        if is_member:
            endpoint = _make_member_endpoint(
                model,
                sp,
                resource=resource,
                db_dep=db_dep,
                pk_param=pk_param,
                nested_vars=nested_vars,
                api=api,
            )
        else:
            endpoint = _make_collection_endpoint(
                model,
                sp,
                resource=resource,
                db_dep=db_dep,
                nested_vars=nested_vars,
                api=api,
            )

        # Status codes
        status_code = _status_for(sp)

        # Capture OUT schema for OpenAPI without enforcing runtime validation
        alias_ns = getattr(getattr(model, "schemas", None), sp.alias, None)
        out_model = getattr(alias_ns, "out", None) if alias_ns else None

        responses_meta = dict(_RESPONSES_META)
        if out_model is not None and status_code != _status.HTTP_204_NO_CONTENT:
            responses_meta[status_code] = {"model": out_model}
            response_class = None
        else:
            responses_meta[status_code] = {"description": "Successful Response"}
            response_class = Response

        # Attach route
        label = f"{model.__name__} - {sp.alias}"
        route_deps = None
        if auth_dep and sp.alias not in allow_anon and sp.target not in allow_anon:
            route_deps = _normalize_deps([auth_dep])

        unique_id = f"{endpoint.__name__}_{uuid4().hex}"
        include_in_schema = bool(
            getattr(sp, "extra", {}).get("include_in_schema", True)
        )
        route_kwargs = dict(
            path=path,
            endpoint=endpoint,
            methods=methods,
            name=f"{model.__name__}.{sp.alias}",
            operation_id=unique_id,
            summary=label,
            description=label,
            response_model=response_model,
            status_code=status_code,
            # IMPORTANT: only class name here; never table name
            tags=list(sp.tags or (model.__name__,)),
            responses=responses_meta,
            include_in_schema=include_in_schema,
        )
        if route_deps:
            route_kwargs["dependencies"] = route_deps
        if response_class is not None:
            route_kwargs["response_class"] = response_class

        secdeps: list[Any] = []
        if auth_dep and sp.alias not in allow_anon and sp.target not in allow_anon:
            if _requires_auth_header(auth_dep):
                secdeps.append(_require_auth_header)
            secdeps.append(auth_dep)
        secdeps.extend(getattr(sp, "secdeps", ()))
        route_secdeps = _normalize_secdeps(secdeps)
        if route_secdeps:
            route_kwargs["dependencies"] = route_secdeps

        if (
            sp.alias != sp.target
            and sp.target in CANON
            and sp.alias != getattr(sp.handler, "__name__", sp.alias)
        ):
            route_kwargs["include_in_schema"] = False

        router.add_api_route(**route_kwargs)

        logger.debug(
            "rest: registered %s %s -> %s.%s (response_model=%s)",
            methods,
            path,
            model.__name__,
            sp.alias,
            getattr(response_model, "__name__", None) if response_model else None,
        )

    return router
