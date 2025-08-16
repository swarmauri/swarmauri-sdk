# autoapi/v3/bindings/rest.py
from __future__ import annotations

import inspect
import logging
from types import SimpleNamespace
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Mapping,
    Optional,
    Sequence,
    Tuple,
)

try:
    from fastapi import APIRouter, Request, Body
    from fastapi import status as _status
except Exception:  # pragma: no cover
    # Minimal shims so the module can be imported without FastAPI
    class APIRouter:  # type: ignore
        def __init__(self, *a, **kw):
            self.routes = []

        def add_api_route(
            self, path: str, endpoint: Callable, methods: Sequence[str], **opts
        ):
            self.routes.append((path, methods, endpoint, opts))

    class Request:  # type: ignore
        def __init__(self, scope=None):
            self.scope = scope or {}
            self.query_params = {}
            self.state = SimpleNamespace()

    def Body(default=None, **kw):  # type: ignore
        return default

    class _status:  # type: ignore
        HTTP_200_OK = 200
        HTTP_201_CREATED = 201


from pydantic import BaseModel

from ..opspec import OpSpec
from ..opspec.types import PHASES
from ..runtime import executor as _executor  # expects _invoke(request, db, phases, ctx)

logger = logging.getLogger(__name__)

_Key = Tuple[str, str]  # (alias, target)


# ───────────────────────────────────────────────────────────────────────────────
# Helpers: resource names, primary keys, schemas, phases, IO shaping
# ───────────────────────────────────────────────────────────────────────────────


def _snake(name: str) -> str:
    out = []
    for i, ch in enumerate(name):
        if ch.isupper() and i and (not name[i - 1].isupper()):
            out.append("_")
        out.append(ch.lower())
    return "".join(out)


def _resource_name(model: type) -> str:
    override = getattr(model, "__resource__", None)
    if override:
        return override
    # Mirror autoapi v2 behavior by deriving the REST resource from the model's
    # class name rather than SQLAlchemy's ``__tablename__`` attribute.  The
    # latter may be pluralized or retain casing (e.g., "Key"), which leads to
    # inconsistent route prefixes like ``/Key`` or ``/key_versions``.  Using the
    # class name ensures predictable snake_case resources across models.
    return _snake(model.__name__)


def _pk_name(model: type) -> str:
    table = getattr(model, "__table__", None)
    if table is None:
        return "id"
    pk = getattr(table, "primary_key", None)
    if pk is None:
        return "id"
    try:
        cols = list(pk.columns)
    except Exception:
        return "id"
    if len(cols) != 1:
        return "id"
    return getattr(cols[0], "name", "id")


def _get_phase_chains(
    model: type, alias: str
) -> Dict[str, Sequence[Callable[..., Awaitable[Any]]]]:
    hooks_root = getattr(model, "hooks", None) or SimpleNamespace()
    alias_ns = getattr(hooks_root, alias, None)
    out: Dict[str, Sequence[Callable[..., Awaitable[Any]]]] = {}
    for ph in PHASES:
        out[ph] = list(getattr(alias_ns, ph, []) or [])
    return out


def _serialize_output(
    model: type, alias: str, target: str, sp: OpSpec, result: Any
) -> Any:
    if sp.returns != "model":
        return result
    schemas_root = getattr(model, "schemas", None)
    if not schemas_root:
        return result
    alias_ns = getattr(schemas_root, alias, None)
    if not alias_ns:
        return result
    out_model = getattr(alias_ns, "out", None)
    if (
        not out_model
        or not inspect.isclass(out_model)
        or not issubclass(out_model, BaseModel)
    ):
        return result
    try:
        if target == "list" and isinstance(result, (list, tuple)):
            return [
                out_model.model_validate(x).model_dump(exclude_none=True)
                for x in result
            ]
        return out_model.model_validate(result).model_dump(exclude_none=True)
    except Exception:
        logger.debug(
            "rest output serialization failed for %s.%s",
            model.__name__,
            alias,
            exc_info=True,
        )
        return result


def _validate_body(
    model: type, alias: str, target: str, body: Mapping[str, Any] | None
) -> Mapping[str, Any]:
    body = body or {}
    schemas_root = getattr(model, "schemas", None)
    if not schemas_root:
        return body
    alias_ns = getattr(schemas_root, alias, None)
    if not alias_ns:
        return body

    in_model = getattr(alias_ns, "in_", None)
    if target in {"list", "clear"}:
        # List/clear use query params primarily; body rarely used
        in_model = getattr(alias_ns, "list", in_model)

    if in_model and inspect.isclass(in_model) and issubclass(in_model, BaseModel):
        try:
            inst = in_model.model_validate(body)  # type: ignore[arg-type]
            return inst.model_dump(exclude_none=True)
        except Exception:
            logger.debug(
                "rest input body validation failed for %s.%s",
                model.__name__,
                alias,
                exc_info=True,
            )
            return body
    return body


def _validate_query(
    model: type, alias: str, target: str, query: Mapping[str, Any]
) -> Mapping[str, Any]:
    schemas_root = getattr(model, "schemas", None)
    if not schemas_root:
        return dict(query)
    alias_ns = getattr(schemas_root, alias, None)
    if not alias_ns:
        return dict(query)
    # For list/clear, prefer .list
    in_model = getattr(
        alias_ns,
        "list",
        None if target not in {"list", "clear"} else getattr(alias_ns, "list", None),
    )
    if in_model and inspect.isclass(in_model) and issubclass(in_model, BaseModel):
        try:
            inst = in_model.model_validate(dict(query))  # type: ignore[arg-type]
            return inst.model_dump(exclude_none=True)
        except Exception:
            logger.debug(
                "rest query validation failed for %s.%s",
                model.__name__,
                alias,
                exc_info=True,
            )
    return dict(query)


# ───────────────────────────────────────────────────────────────────────────────
# Routing strategy
# ───────────────────────────────────────────────────────────────────────────────

_DEFAULT_METHODS: Dict[str, Tuple[str, ...]] = {
    "create": ("POST",),
    "read": ("GET",),
    "update": ("PATCH",),
    "replace": ("PUT",),
    "delete": ("DELETE",),
    "list": ("GET",),
    "clear": ("DELETE",),
    "bulk_create": ("POST",),
    "bulk_update": ("PATCH",),
    "bulk_replace": ("PUT",),
    "bulk_delete": ("DELETE",),
    "custom": ("POST",),  # default for custom ops
}


def _default_path_suffix(sp: OpSpec) -> str | None:
    if sp.target.startswith("bulk_"):
        return "/bulk"
    if sp.target == "custom":
        return f"/{sp.alias}"
    return None


def _path_for_spec(
    model: type, sp: OpSpec, *, resource: str, pk_param: str = "item_id"
) -> Tuple[str, bool]:
    """
    Return (path, is_member). We use a generic {item_id} placeholder for all member ops
    and remap it to the model's real PK name inside ``ctx.path_params``.
    """
    suffix = sp.path_suffix or _default_path_suffix(sp) or ""
    if not suffix.startswith("/") and suffix:
        suffix = "/" + suffix

    if sp.arity == "member" or sp.target in {"read", "update", "replace", "delete"}:
        return f"/{resource}/{{{pk_param}}}{suffix}", True
    return f"/{resource}{suffix}", False


def _response_model_for(sp: OpSpec, model: type) -> Any | None:
    if sp.returns != "model":
        return None
    alias_ns = getattr(
        getattr(model, "schemas", None) or SimpleNamespace(), sp.alias, None
    )
    out_model = getattr(alias_ns, "out", None)
    if out_model is None:
        return None
    # For list, FastAPI can accept typing.List[out_model]
    if sp.target == "list":
        from typing import List as _List

        try:
            return _List[out_model]  # type: ignore[index]
        except Exception:
            return None
    return out_model


# ───────────────────────────────────────────────────────────────────────────────
# Endpoint factories
# ───────────────────────────────────────────────────────────────────────────────


def _make_collection_endpoint(
    model: type, sp: OpSpec, *, resource: str
) -> Callable[..., Awaitable[Any]]:
    alias = sp.alias
    target = sp.target

    async def _endpoint(
        request: Request,
        db: Any,
        body: Mapping[str, Any] | None = Body(default=None),
    ):
        # Build payload from query for list/clear; otherwise from body
        if target in {"list", "clear"}:
            raw_query = dict(request.query_params)
            payload = _validate_query(model, alias, target, raw_query)
        else:
            payload = _validate_body(model, alias, target, body)

        # Compose ctx
        ctx: Dict[str, Any] = {
            "request": request,
            "db": db,
            "payload": payload,
            "path_params": {},  # no member id
            "env": SimpleNamespace(
                method=alias, params=payload, target=target, model=model
            ),
        }
        phases = _get_phase_chains(model, alias)

        result = await _executor._invoke(
            request=request,
            db=db,
            phases=phases,
            ctx=ctx,
        )
        return _serialize_output(model, alias, target, sp, result)

    _endpoint.__name__ = f"rest_{model.__name__}_{alias}_collection"
    _endpoint.__qualname__ = _endpoint.__name__
    _endpoint.__doc__ = (
        f"REST collection endpoint for {model.__name__}.{alias} ({target})"
    )
    return _endpoint


def _make_member_endpoint(
    model: type, sp: OpSpec, *, resource: str, pk_param: str = "item_id"
) -> Callable[..., Awaitable[Any]]:
    alias = sp.alias
    target = sp.target
    real_pk = _pk_name(model)

    async def _endpoint(
        item_id: Any,
        request: Request,
        db: Any,
        body: Mapping[str, Any] | None = Body(default=None),
    ):
        payload = _validate_body(model, alias, target, body)

        ctx: Dict[str, Any] = {
            "request": request,
            "db": db,
            "payload": payload,
            # map generic item_id to real PK column name for handler resolution
            "path_params": {real_pk: item_id, pk_param: item_id},
            "env": SimpleNamespace(
                method=alias, params=payload, target=target, model=model
            ),
        }
        phases = _get_phase_chains(model, alias)

        result = await _executor._invoke(
            request=request,
            db=db,
            phases=phases,
            ctx=ctx,
        )
        return _serialize_output(model, alias, target, sp, result)

    _endpoint.__name__ = f"rest_{model.__name__}_{alias}_member"
    _endpoint.__qualname__ = _endpoint.__name__
    _endpoint.__doc__ = f"REST member endpoint for {model.__name__}.{alias} ({target})"
    return _endpoint


# ───────────────────────────────────────────────────────────────────────────────
# Router builder
# ───────────────────────────────────────────────────────────────────────────────


def _build_router(model: type, specs: Sequence[OpSpec]) -> APIRouter:
    resource = _resource_name(model)
    router = APIRouter()
    pk_param = "item_id"

    for sp in specs:
        if not sp.expose_routes:
            continue

        # Determine path and membership
        path, is_member = _path_for_spec(
            model, sp, resource=resource, pk_param=pk_param
        )

        # HTTP methods
        methods = list(sp.http_methods or _DEFAULT_METHODS.get(sp.target, ("POST",)))
        response_model = _response_model_for(sp, model)

        # Build endpoint
        if is_member:
            endpoint = _make_member_endpoint(
                model, sp, resource=resource, pk_param=pk_param
            )
        else:
            endpoint = _make_collection_endpoint(model, sp, resource=resource)

        # Default status code (201 for create on collection; else 200)
        status_code = (
            _status.HTTP_201_CREATED
            if sp.target == "create" and not is_member
            else _status.HTTP_200_OK
        )

        # Attach route
        label = f"{model.__name__} - {sp.alias}"
        router.add_api_route(
            path,
            endpoint,
            methods=methods,
            name=f"{model.__name__}.{sp.alias}",
            summary=label,
            description=label,
            response_model=response_model,
            status_code=status_code,
            tags=list(sp.tags or (resource,)),
        )

        logger.debug(
            "rest: registered %s %s -> %s.%s (response_model=%s)",
            methods,
            path,
            model.__name__,
            sp.alias,
            getattr(response_model, "__name__", None) if response_model else None,
        )

    return router


# ───────────────────────────────────────────────────────────────────────────────
# Public API
# ───────────────────────────────────────────────────────────────────────────────


def build_router_and_attach(
    model: type, specs: Sequence[OpSpec], *, only_keys: Optional[Sequence[_Key]] = None
) -> None:
    """
    Build an APIRouter for the model and attach it to `model.rest.router`.
    For simplicity and correctness with FastAPI, we **rebuild the entire router**
    on each call (FastAPI does not support removing individual routes cleanly).
    """
    router = _build_router(model, specs)
    rest_ns = getattr(model, "rest", None) or SimpleNamespace()
    rest_ns.router = router
    setattr(model, "rest", rest_ns)
    logger.debug(
        "rest: %s router attached with %d routes",
        model.__name__,
        len(getattr(router, "routes", []) or []),
    )


__all__ = ["build_router_and_attach"]
