# autoapi/v3/bindings/rest.py
from __future__ import annotations

import inspect
import logging
import re
import typing as _typing
from types import SimpleNamespace
from typing import (
    Annotated,
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
)

from typing import get_origin as _get_origin, get_args as _get_args

try:
    from ..types import (
        Router,
        Request,
        Body,
        Depends,
        HTTPException,
        Response,
        Path,
        Security,
    )
    from fastapi import Query
    from fastapi import status as _status
except Exception:  # pragma: no cover
    # Minimal shims so the module can be imported without FastAPI
    class Router:  # type: ignore
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

    def Depends(fn):  # type: ignore
        return fn

    def Security(fn):  # type: ignore
        return fn

    def Query(default=None, **kw):  # type: ignore
        return default

    class HTTPException(Exception):  # type: ignore
        def __init__(self, status_code: int, detail: str | None = None):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    class Response:  # type: ignore
        def __init__(self, *a, **kw):
            pass

    class _status:  # type: ignore
        HTTP_200_OK = 200
        HTTP_201_CREATED = 201
        HTTP_204_NO_CONTENT = 204
        HTTP_400_BAD_REQUEST = 400
        HTTP_401_UNAUTHORIZED = 401
        HTTP_403_FORBIDDEN = 403
        HTTP_404_NOT_FOUND = 404
        HTTP_409_CONFLICT = 409
        HTTP_422_UNPROCESSABLE_ENTITY = 422
        HTTP_429_TOO_MANY_REQUESTS = 429
        HTTP_500_INTERNAL_SERVER_ERROR = 500


from pydantic import BaseModel, Field, create_model

from ..opspec import OpSpec
from ..opspec.types import PHASES
from ..runtime import executor as _executor  # expects _invoke(request, db, phases, ctx)

# Prefer Kernel phase-chains if available
try:
    from ..runtime.kernel import build_phase_chains as _kernel_build_phase_chains  # type: ignore
except Exception:  # pragma: no cover
    _kernel_build_phase_chains = None  # type: ignore

from ..config.constants import (
    AUTOAPI_GET_ASYNC_DB_ATTR,
    AUTOAPI_GET_DB_ATTR,
    AUTOAPI_AUTH_DEP_ATTR,
    AUTOAPI_REST_DEPENDENCIES_ATTR,
    AUTOAPI_ALLOW_ANON_ATTR,
)
from ..rest import _nested_prefix
from ..schema.builder import _strip_parent_fields

logger = logging.getLogger(__name__)

_Key = Tuple[str, str]  # (alias, target)


def _ensure_jsonable(obj: Any) -> Any:
    """Best-effort conversion of DB rows, row-mappings, or ORM objects to dicts."""
    if isinstance(obj, (list, tuple)):
        return [_ensure_jsonable(x) for x in obj]

    if isinstance(obj, Mapping):
        try:
            return {k: _ensure_jsonable(v) for k, v in dict(obj).items()}
        except Exception:  # pragma: no cover - fall back to original object
            pass

    try:
        data = vars(obj)
    except TypeError:
        return obj

    return {k: _ensure_jsonable(v) for k, v in data.items() if not k.startswith("_")}


def _req_state_db(request: Request) -> Any:
    return getattr(request.state, "db", None)


# ───────────────────────────────────────────────────────────────────────────────
# Helpers: resource names, primary keys, schemas, phases, IO shaping
# ───────────────────────────────────────────────────────────────────────────────


def _resource_name(model: type) -> str:
    """
    Resource segment for HTTP paths/tags.

    IMPORTANT: Never use table name here. Only allow an explicit __resource__
    override or fall back to the model class name in lowercase.
    """
    override = getattr(model, "__resource__", None)
    return override or model.__name__.lower()


def _pk_name(model: type) -> str:
    """
    Single primary key name (fallback 'id'). For composite keys, still returns 'id'.
    Used for backward-compat path-param aliasing and handler resolution.
    """
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


def _pk_names(model: type) -> set[str]:
    """All PK column names (fallback {'id'})."""
    table = getattr(model, "__table__", None)
    try:
        cols = getattr(getattr(table, "primary_key", None), "columns", None)
        if cols is None:
            return {"id"}
        out = {getattr(c, "name", None) for c in cols}
        out.discard(None)
        return out or {"id"}
    except Exception:
        return {"id"}


def _get_phase_chains(
    model: type, alias: str
) -> Dict[str, Sequence[Callable[..., Awaitable[Any]]]]:
    """
    Prefer building via runtime Kernel (atoms + system steps + hooks in one lifecycle).
    Fallback: read the pre-built model.hooks.<alias> chains directly.
    """
    if _kernel_build_phase_chains is not None:
        try:
            return _kernel_build_phase_chains(model, alias)
        except Exception:
            logger.exception(
                "Kernel build_phase_chains failed for %s.%s; falling back to hooks",
                getattr(model, "__name__", model),
                alias,
            )
    hooks_root = getattr(model, "hooks", None) or SimpleNamespace()
    alias_ns = getattr(hooks_root, alias, None)
    out: Dict[str, Sequence[Callable[..., Awaitable[Any]]]] = {}
    for ph in PHASES:
        out[ph] = list(getattr(alias_ns, ph, []) or [])
    return out


def _serialize_output(
    model: type, alias: str, target: str, sp: OpSpec, result: Any
) -> Any:
    """
    If a response schema exists (model.schemas.<alias>.out), serialize to it.
    Otherwise, attempt a best-effort conversion to primitive types so FastAPI
    can JSON-encode the response.
    """

    def _final(val: Any) -> Any:
        if target == "list" and isinstance(val, (list, tuple)):
            return [_ensure_jsonable(v) for v in val]
        return _ensure_jsonable(val)

    schemas_root = getattr(model, "schemas", None)
    if not schemas_root:
        return _final(result)
    alias_ns = getattr(schemas_root, alias, None)
    if not alias_ns:
        return _final(result)
    out_model = getattr(alias_ns, "out", None)
    if (
        not out_model
        or not inspect.isclass(out_model)
        or not issubclass(out_model, BaseModel)
    ):
        return _final(result)
    try:
        if target == "list" and isinstance(result, (list, tuple)):
            return [
                out_model.model_validate(x).model_dump(exclude_none=True, by_alias=True)
                for x in result
            ]
        return out_model.model_validate(result).model_dump(
            exclude_none=True, by_alias=True
        )
    except Exception:
        logger.debug(
            "rest output serialization failed for %s.%s",
            model.__name__,
            alias,
            exc_info=True,
        )
        return _final(result)


def _validate_body(
    model: type, alias: str, target: str, body: Any | None
) -> Mapping[str, Any] | Sequence[Mapping[str, Any]]:
    """Normalize and validate the incoming request body.

    Accepts dict-like payloads or sequences of dict-like payloads for bulk
    operations. If the AutoAPI schemas define a request model, use it for
    validation; otherwise return the payload as-is (coerced to a
    ``dict``/``list`` when possible).
    """
    if isinstance(body, BaseModel):
        return body.model_dump(exclude_none=True)

    # Bulk mutations expect a list payload (bulk_create/bulk_update/bulk_replace/bulk_merge).
    if target in {"bulk_create", "bulk_update", "bulk_replace", "bulk_merge"}:
        items: Sequence[Any] = body or []
        if not isinstance(items, Sequence) or isinstance(items, (str, bytes)):
            items = []

        schemas_root = getattr(model, "schemas", None)
        alias_ns = getattr(schemas_root, alias, None) if schemas_root else None
        in_item = getattr(alias_ns, "in_item", None) if alias_ns else None

        out: list[Mapping[str, Any]] = []
        for item in items:
            if isinstance(item, BaseModel):
                out.append(item.model_dump(exclude_none=True))
                continue
            data: Mapping[str, Any] | None = None
            if in_item and inspect.isclass(in_item) and issubclass(in_item, BaseModel):
                try:
                    inst = in_item.model_validate(item)  # type: ignore[arg-type]
                    data = inst.model_dump(exclude_none=True)
                except Exception:
                    logger.debug(
                        "rest input body validation failed for %s.%s",
                        model.__name__,
                        alias,
                        exc_info=True,
                    )
            if data is None:
                data = dict(item) if isinstance(item, Mapping) else {}
            out.append(data)
        return out

    if (
        target in {"create", "update", "replace", "merge"}
        and isinstance(body, Sequence)
        and not isinstance(body, (str, bytes, Mapping))
    ):
        # Treat sequence payloads as bulk mutations using the corresponding bulk schema
        bulk_target = f"bulk_{target}"
        items: Sequence[Any] = body
        schemas_root = getattr(model, "schemas", None)
        alias_ns = getattr(schemas_root, bulk_target, None) if schemas_root else None
        in_item = getattr(alias_ns, "in_item", None) if alias_ns else None

        out: list[Mapping[str, Any]] = []
        for item in items:
            if isinstance(item, BaseModel):
                out.append(item.model_dump(exclude_none=True))
                continue
            data: Mapping[str, Any] | None = None
            if in_item and inspect.isclass(in_item) and issubclass(in_item, BaseModel):
                try:
                    inst = in_item.model_validate(item)  # type: ignore[arg-type]
                    data = inst.model_dump(exclude_none=True)
                except Exception:
                    logger.debug(
                        "rest input body validation failed for %s.%s",
                        model.__name__,
                        bulk_target,
                        exc_info=True,
                    )
            if data is None:
                data = dict(item) if isinstance(item, Mapping) else {}
            out.append(data)
        return out

    body = body or {}
    if not isinstance(body, Mapping):
        body = {}

    schemas_root = getattr(model, "schemas", None)
    if not schemas_root:
        return dict(body)
    alias_ns = getattr(schemas_root, alias, None)
    if not alias_ns:
        return dict(body)
    in_model = getattr(alias_ns, "in_", None)

    if in_model and inspect.isclass(in_model) and issubclass(in_model, BaseModel):
        try:
            inst = in_model.model_validate(body)  # type: ignore[arg-type]
            return inst.model_dump(exclude_none=True)
        except Exception as e:
            logger.debug(
                "rest input body validation failed for %s.%s",
                model.__name__,
                alias,
                exc_info=True,
            )
            raise HTTPException(
                status_code=_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e),
            )
    return dict(body)


def _validate_query(
    model: type, alias: str, target: str, query: Mapping[str, Any]
) -> Mapping[str, Any]:
    """
    Validate list/clear inputs coming from the query string. We avoid instantiating
    the model when the user supplied no filters, to prevent any schema defaults
    (possibly invalid) from being applied.
    """
    # If nothing was supplied, don't instantiate the model (avoids bad defaults).
    if not query or (isinstance(query, Mapping) and len(query) == 0):
        return {}

    schemas_root = getattr(model, "schemas", None)
    if not schemas_root:
        return dict(query)
    alias_ns = getattr(schemas_root, alias, None)
    if not alias_ns:
        return dict(query)
    in_model = getattr(alias_ns, "in_", None)

    # If there's a Pydantic model, map aliases->field names before validation.
    if in_model and inspect.isclass(in_model) and issubclass(in_model, BaseModel):
        try:
            fields = getattr(in_model, "model_fields", {})
            data: Dict[str, Any] = {}
            for name, f in fields.items():
                alias_key = getattr(f, "alias", None) or name
                # Prefer alias if present; else accept field name
                if alias_key in query:
                    val = query[alias_key]
                elif name in query:
                    val = query[name]
                else:
                    continue
                # Drop "unset" values (None, empty string, empty list/tuple/set)
                if val is None:
                    continue
                if isinstance(val, str) and not val.strip():
                    continue
                if isinstance(val, (list, tuple, set)) and len(val) == 0:
                    continue
                data[name] = val

            if not data:
                return {}

            inst = in_model.model_validate(data)  # type: ignore[arg-type]
            return inst.model_dump(exclude_none=True)
        except Exception as e:
            # Surface invalid user-supplied filters as 422
            raise HTTPException(
                status_code=_status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
            )
    # No model — pass through what was provided
    return dict(query)


def _normalize_deps(deps: Optional[Sequence[Any]]) -> list[Any]:
    """Turn callables into Depends(...) unless already a dependency object."""
    if not deps:
        return []
    out: list[Any] = []
    for d in deps:
        is_dep_obj = getattr(d, "dependency", None) is not None
        out.append(d if is_dep_obj else Depends(d))
    return out


def _normalize_secdeps(secdeps: Optional[Sequence[Any]]) -> list[Any]:
    """Turn callables into Security(...) unless already a dependency object."""
    if not secdeps:
        return []
    out: list[Any] = []
    for d in secdeps:
        is_dep_obj = getattr(d, "dependency", None) is not None
        out.append(d if is_dep_obj else Security(d))
    return out


def _status_for(sp: OpSpec) -> int:
    if sp.status_code is not None:
        return sp.status_code
    target = sp.target
    if target == "create":
        # Creating resources should use HTTP 201 (Created).
        # Earlier revisions defaulted to 200 for backward compatibility, but
        # the integration tests rely on the standard 201 code.
        return _status.HTTP_201_CREATED
    if target in ("delete", "clear"):
        # DELETE operations return a confirmation payload (e.g. number of
        # deleted rows). Returning 204 would discard this body, so default to
        # 200 to surface the response content to clients.
        return _status.HTTP_200_OK
    return _status.HTTP_200_OK


_RESPONSES_META = {
    400: {"description": "Bad Request"},
    401: {"description": "Unauthorized"},
    403: {"description": "Forbidden"},
    404: {"description": "Not Found"},
    409: {"description": "Conflict"},
    422: {"description": "Unprocessable Entity"},
    429: {"description": "Too Many Requests"},
    500: {"description": "Internal Server Error"},
}

# ───────────────────────────────────────────────────────────────────────────────
# Routing strategy
# ───────────────────────────────────────────────────────────────────────────────

_DEFAULT_METHODS: Dict[str, Tuple[str, ...]] = {
    "create": ("POST",),
    "read": ("GET",),
    "update": ("PATCH",),
    "replace": ("PUT",),
    "merge": ("PATCH",),
    "delete": ("DELETE",),
    "list": ("GET",),
    "clear": ("DELETE",),
    "bulk_create": ("POST",),
    "bulk_update": ("PATCH",),
    "bulk_replace": ("PUT",),
    "bulk_merge": ("PATCH",),
    "bulk_delete": ("DELETE",),
    "custom": ("POST",),  # default for custom ops
}


def _default_path_suffix(sp: OpSpec) -> str | None:
    if sp.target.startswith("bulk_"):
        # Bulk operations now share the same collection path as their
        # single-record counterparts.
        return None
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
    """
    Determine the FastAPI response_model based on presence of an out schema.
    If there is no out schema, return None (raw pass-through).
    Suppress response_model for delete routes which may return 204.
    """
    if sp.target == "delete":
        return None
    alias_ns = getattr(
        getattr(model, "schemas", None) or SimpleNamespace(), sp.alias, None
    )
    out_model = getattr(alias_ns, "out", None)
    if out_model is None:
        return None
    # For list, FastAPI can accept typing-style list[out_model]
    if sp.target == "list":
        try:
            return list[out_model]  # type: ignore[index]
        except Exception:
            return None
    return out_model


def _request_model_for(sp: OpSpec, model: type) -> Any | None:
    """Fetch the request model for docs and validation."""
    alias_ns = getattr(
        getattr(model, "schemas", None) or SimpleNamespace(), sp.alias, None
    )
    return getattr(alias_ns, "in_", None)


# ───────────────────────────────────────────────────────────────────────────────
# Query param dependency (so OpenAPI shows list filters)
# ───────────────────────────────────────────────────────────────────────────────


def _strip_optional(t: Any) -> Any:
    """If annotation is Optional[T] (i.e., Union[T, None]), return T; else return the input."""
    origin = _get_origin(t)
    if origin is _typing.Union:
        args = tuple(a for a in _get_args(t) if a is not type(None))
        return args[0] if len(args) == 1 else Any
    return t


def _make_list_query_dep(model: type, alias: str):
    """
    Build a dependency whose signature exposes Query(...) params derived from
    schemas.<alias>.in_ fields, so FastAPI documents them in OpenAPI. The dep
    returns raw user-supplied values; we validate later in _validate_query().
    """
    alias_ns = getattr(
        getattr(model, "schemas", None) or SimpleNamespace(), alias, None
    )
    in_model = getattr(alias_ns, "in_", None)

    # If no model, return raw query as-is
    if not (in_model and inspect.isclass(in_model) and issubclass(in_model, BaseModel)):

        def _dep(request: Request) -> Dict[str, Any]:
            return dict(request.query_params)

        _dep.__name__ = f"list_params_{model.__name__}_{alias}"
        return _dep

    fields = getattr(in_model, "model_fields", {})

    def _dep(**raw: Any) -> Dict[str, Any]:
        """Collect only user-supplied values; never apply schema defaults here."""
        data: Dict[str, Any] = {}
        for name, f in fields.items():
            key = getattr(f, "alias", None) or name
            if key not in raw:
                continue
            val = raw[key]
            # drop "unset" values
            if val is None:
                continue
            if isinstance(val, str) and not val.strip():
                continue
            if isinstance(val, (list, tuple, set)) and len(val) == 0:
                continue
            data[key] = val
        return data  # raw; validation happens in _validate_query

    # Build signature with Query(None) so OpenAPI shows optional filters
    params: list[inspect.Parameter] = []
    for name, f in fields.items():
        key = getattr(f, "alias", None) or name
        ann = getattr(f, "annotation", Any)
        base = _strip_optional(ann)
        origin = _get_origin(base)
        if origin in (list, tuple, set):
            inner = (_get_args(base) or (str,))[0]
            annotation = list[inner] | None  # type: ignore[index]
        else:
            annotation = base | None
        default_q = Query(None, description=getattr(f, "description", None))
        params.append(
            inspect.Parameter(
                name=key,
                kind=inspect.Parameter.KEYWORD_ONLY,
                default=default_q,
                annotation=annotation,
            )
        )

    _dep.__signature__ = inspect.Signature(
        parameters=params, return_annotation=Dict[str, Any]
    )
    _dep.__name__ = f"list_params_{model.__name__}_{alias}"
    return _dep


# ───────────────────────────────────────────────────────────────────────────────
# Optionalize list.in_ model (hardening against bad defaults)
# ───────────────────────────────────────────────────────────────────────────────


def _optionalize_list_in_model(in_model: type[BaseModel]) -> type[BaseModel]:
    """
    Build a drop-in replacement of `in_model` where every field is Optional[...] with default=None.
    This prevents bogus defaults (like 'string' on enums) from being applied when no filters are supplied.
    """
    try:
        fields = getattr(in_model, "model_fields", {})
    except Exception:
        return in_model

    defs: Dict[str, tuple[Any, Any]] = {}
    for name, f in fields.items():
        ann = getattr(f, "annotation", Any)
        opt_ann = _typing.Union[ann, type(None)]  # Optional[ann]
        defs[name] = (
            opt_ann,
            Field(
                default=None,
                alias=getattr(f, "alias", None),
                description=getattr(f, "description", None),
            ),
        )

    New = create_model(  # type: ignore[misc]
        f"{in_model.__name__}__Optionalized",
        **defs,
    )
    # Flag to avoid re-optionalizing
    setattr(New, "__autoapi_optionalized__", True)
    return New


def _coerce_parent_kw(model: type, parent_kw: Dict[str, Any]) -> None:
    for name, val in list(parent_kw.items()):
        col = getattr(model, name, None)
        try:
            parent_kw[name] = col.type.python_type(val)  # type: ignore[attr-defined]
        except Exception:
            pass


# ───────────────────────────────────────────────────────────────────────────────
# Endpoint factories (split by body/no-body and member/collection)
# ───────────────────────────────────────────────────────────────────────────────


def _make_collection_endpoint(
    model: type,
    sp: OpSpec,
    *,
    resource: str,
    db_dep: Callable[..., Any],
    nested_vars: Sequence[str] | None = None,
) -> Callable[..., Awaitable[Any]]:
    alias = sp.alias
    target = sp.target
    nested_vars = list(nested_vars or [])

    # --- No body on GET list / DELETE clear ---
    if target in {"list", "clear"}:
        if target == "list":
            list_dep = _make_list_query_dep(model, alias)

            async def _endpoint(
                request: Request,
                q: Mapping[str, Any] = Depends(list_dep),
                db: Any = Depends(db_dep),
                **kw: Any,
            ):
                parent_kw = {k: kw[k] for k in nested_vars if k in kw}
                _coerce_parent_kw(model, parent_kw)
                query = dict(q)
                query.update(parent_kw)
                payload = _validate_query(model, alias, target, query)
                ctx: Dict[str, Any] = {
                    "request": request,
                    "db": db,
                    "payload": payload,
                    "path_params": parent_kw,
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

            params = [
                inspect.Parameter(
                    nv,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[str, Path(...)],
                )
                for nv in nested_vars
            ]
            params.extend(
                [
                    inspect.Parameter(
                        "request",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=Request,
                    ),
                    inspect.Parameter(
                        "q",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=Annotated[Mapping[str, Any], Depends(list_dep)],
                    ),
                    inspect.Parameter(
                        "db",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=Annotated[Any, Depends(db_dep)],
                    ),
                ]
            )
            _endpoint.__signature__ = inspect.Signature(params)
        else:

            async def _endpoint(
                request: Request,
                db: Any = Depends(db_dep),
                **kw: Any,
            ):
                parent_kw = {k: kw[k] for k in nested_vars if k in kw}
                _coerce_parent_kw(model, parent_kw)
                payload: Mapping[str, Any] = dict(parent_kw)
                ctx: Dict[str, Any] = {
                    "request": request,
                    "db": db,
                    "payload": payload,
                    "path_params": parent_kw,
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

            params = [
                inspect.Parameter(
                    nv,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[str, Path(...)],
                )
                for nv in nested_vars
            ]
            params.extend(
                [
                    inspect.Parameter(
                        "request",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=Request,
                    ),
                    inspect.Parameter(
                        "db",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=Annotated[Any, Depends(db_dep)],
                    ),
                ]
            )
            _endpoint.__signature__ = inspect.Signature(params)

        _endpoint.__name__ = f"rest_{model.__name__}_{alias}_collection"
        _endpoint.__qualname__ = _endpoint.__name__
        _endpoint.__doc__ = (
            f"REST collection endpoint for {model.__name__}.{alias} ({target})"
        )
        # NOTE: do NOT set body annotation for no-body endpoints
        return _endpoint

    # --- Body-based collection endpoints: create / bulk_* ---

    body_model = _request_model_for(sp, model)
    base_annotation = body_model if body_model is not None else Mapping[str, Any]

    if target in {"bulk_create", "bulk_update", "bulk_replace", "bulk_merge"}:
        alias_ns = getattr(
            getattr(model, "schemas", None) or SimpleNamespace(), alias, None
        )
        item_model = getattr(alias_ns, "in_item", None) if alias_ns else None
        if (
            item_model
            and inspect.isclass(item_model)
            and issubclass(item_model, BaseModel)
        ):
            try:
                body_annotation = list[item_model]  # type: ignore[valid-type]
            except Exception:  # pragma: no cover - best effort
                body_annotation = List[item_model]  # type: ignore[name-defined]
        elif body_model is None:
            try:
                body_annotation = list[Mapping[str, Any]]  # type: ignore[valid-type]
            except Exception:  # pragma: no cover - best effort
                body_annotation = List[Mapping[str, Any]]  # type: ignore[name-defined]
        else:
            body_annotation = base_annotation
    else:
        if target in {"create", "update", "replace", "merge"}:
            try:
                list_ann = list[Mapping[str, Any]]  # type: ignore[valid-type]
            except Exception:  # pragma: no cover - best effort
                list_ann = List[Mapping[str, Any]]  # type: ignore[name-defined]
            if body_model is not None:
                try:
                    body_annotation = body_model | list_ann  # type: ignore[operator]
                except Exception:  # pragma: no cover - best effort
                    from typing import Union as _Union

                    body_annotation = _Union[body_model, list_ann]
            else:
                try:
                    body_annotation = Mapping[str, Any] | list_ann  # type: ignore[operator]
                except Exception:  # pragma: no cover - best effort
                    from typing import Union as _Union

                    body_annotation = _Union[Mapping[str, Any], list_ann]
        else:
            body_annotation = base_annotation

    async def _endpoint(
        request: Request,
        db: Any = Depends(db_dep),
        body=Body(...),
        **kw: Any,
    ):
        parent_kw = {k: kw[k] for k in nested_vars if k in kw}
        _coerce_parent_kw(model, parent_kw)
        payload = _validate_body(model, alias, target, body)
        exec_alias = alias
        exec_target = target
        if (
            target in {"create", "update", "replace", "merge"}
            and isinstance(payload, Sequence)
            and not isinstance(payload, Mapping)
        ):
            exec_alias = f"bulk_{target}"
            exec_target = f"bulk_{target}"
        if parent_kw:
            if isinstance(payload, Mapping):
                payload = dict(payload)
                payload.update(parent_kw)
            else:
                payload = parent_kw
        ctx: Dict[str, Any] = {
            "request": request,
            "db": db,
            "payload": payload,
            "path_params": parent_kw,
            "env": SimpleNamespace(
                method=exec_alias, params=payload, target=exec_target, model=model
            ),
        }
        ctx["response_serializer"] = lambda r: _serialize_output(
            model, exec_alias, exec_target, sp, r
        )
        phases = _get_phase_chains(model, exec_alias)
        result = await _executor._invoke(
            request=request,
            db=db,
            phases=phases,
            ctx=ctx,
        )
        return result

    params = [
        inspect.Parameter(
            nv,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[str, Path(...)],
        )
        for nv in nested_vars
    ]
    params.extend(
        [
            inspect.Parameter(
                "request",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Request,
            ),
            inspect.Parameter(
                "db",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[Any, Depends(db_dep)],
            ),
            inspect.Parameter(
                "body",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[body_annotation, Body(...)],
            ),
        ]
    )
    _endpoint.__signature__ = inspect.Signature(params)

    _endpoint.__name__ = f"rest_{model.__name__}_{alias}_collection"
    _endpoint.__qualname__ = _endpoint.__name__
    _endpoint.__doc__ = (
        f"REST collection endpoint for {model.__name__}.{alias} ({target})"
    )
    _endpoint.__annotations__["body"] = body_annotation
    return _endpoint


def _make_member_endpoint(
    model: type,
    sp: OpSpec,
    *,
    resource: str,
    db_dep: Callable[..., Any],
    pk_param: str = "item_id",
    nested_vars: Sequence[str] | None = None,
) -> Callable[..., Awaitable[Any]]:
    alias = sp.alias
    target = sp.target
    real_pk = _pk_name(model)
    pk_names = _pk_names(model)
    nested_vars = list(nested_vars or [])

    # --- No body on GET read / DELETE delete ---
    if target in {"read", "delete"}:

        async def _endpoint(
            item_id: Any,
            request: Request,
            db: Any = Depends(db_dep),
            **kw: Any,
        ):
            parent_kw = {k: kw[k] for k in nested_vars if k in kw}
            _coerce_parent_kw(model, parent_kw)
            payload: Mapping[str, Any] = dict(parent_kw)
            path_params = {real_pk: item_id, pk_param: item_id, **parent_kw}
            ctx: Dict[str, Any] = {
                "request": request,
                "db": db,
                "payload": payload,
                "path_params": path_params,
                "env": SimpleNamespace(
                    method=alias, params=payload, target=target, model=model
                ),
            }
            ctx["response_serializer"] = lambda r: _serialize_output(
                model, alias, target, sp, r
            )
            phases = _get_phase_chains(model, alias)
            result = await _executor._invoke(
                request=request,
                db=db,
                phases=phases,
                ctx=ctx,
            )
            return result

        params = [
            inspect.Parameter(
                nv,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[str, Path(...)],
            )
            for nv in nested_vars
        ]
        params.extend(
            [
                inspect.Parameter(
                    "item_id",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[Any, Path(...)],
                ),
                inspect.Parameter(
                    "request",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Request,
                ),
                inspect.Parameter(
                    "db",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[Any, Depends(db_dep)],
                ),
            ]
        )
        _endpoint.__signature__ = inspect.Signature(params)

        _endpoint.__name__ = f"rest_{model.__name__}_{alias}_member"
        _endpoint.__qualname__ = _endpoint.__name__
        _endpoint.__doc__ = (
            f"REST member endpoint for {model.__name__}.{alias} ({target})"
        )
        # NOTE: do NOT set body annotation for no-body endpoints
        return _endpoint

    body_model = _request_model_for(sp, model)
    if body_model is None and sp.request_model is None and target == "custom":

        async def _endpoint(
            item_id: Any,
            request: Request,
            db: Any = Depends(db_dep),
            **kw: Any,
        ):
            parent_kw = {k: kw[k] for k in nested_vars if k in kw}
            _coerce_parent_kw(model, parent_kw)
            payload: Mapping[str, Any] = dict(parent_kw)
            path_params = {real_pk: item_id, pk_param: item_id, **parent_kw}
            ctx: Dict[str, Any] = {
                "request": request,
                "db": db,
                "payload": payload,
                "path_params": path_params,
                "env": SimpleNamespace(
                    method=alias, params=payload, target=target, model=model
                ),
            }
            ctx["response_serializer"] = lambda r: _serialize_output(
                model, alias, target, sp, r
            )
            phases = _get_phase_chains(model, alias)
            result = await _executor._invoke(
                request=request,
                db=db,
                phases=phases,
                ctx=ctx,
            )
            return result

        params = [
            inspect.Parameter(
                nv,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[str, Path(...)],
            )
            for nv in nested_vars
        ]
        params.extend(
            [
                inspect.Parameter(
                    "item_id",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[Any, Path(...)],
                ),
                inspect.Parameter(
                    "request",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Request,
                ),
                inspect.Parameter(
                    "db",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[Any, Depends(db_dep)],
                ),
            ]
        )
        _endpoint.__signature__ = inspect.Signature(params)

        _endpoint.__name__ = f"rest_{model.__name__}_{alias}_member"
        _endpoint.__qualname__ = _endpoint.__name__
        _endpoint.__doc__ = (
            f"REST member endpoint for {model.__name__}.{alias} ({target})"
        )
        return _endpoint

    # --- Body-based member endpoints: PATCH update / PUT replace (and custom member) ---

    if body_model is None:
        body_annotation = Optional[Mapping[str, Any]]
        body_default = Body(None)
    else:
        body_annotation = body_model
        body_default = Body(...)

    async def _endpoint(
        item_id: Any,
        request: Request,
        db: Any = Depends(db_dep),
        body=body_default,
        **kw: Any,
    ):
        parent_kw = {k: kw[k] for k in nested_vars if k in kw}
        _coerce_parent_kw(model, parent_kw)
        payload = _validate_body(model, alias, target, body)

        # Enforce path-PK canonicality. If body echoes PK: drop if equal, 409 if mismatch.
        for k in pk_names:
            if k in payload:
                if str(payload[k]) != str(item_id) and len(pk_names) == 1:
                    raise HTTPException(
                        status_code=_status.HTTP_409_CONFLICT,
                        detail=f"Identifier mismatch for '{k}': path={item_id}, body={payload[k]}",
                    )
                payload.pop(k, None)
        payload.pop(pk_param, None)
        if parent_kw:
            payload.update(parent_kw)

        path_params = {real_pk: item_id, pk_param: item_id, **parent_kw}

        ctx: Dict[str, Any] = {
            "request": request,
            "db": db,
            "payload": payload,
            "path_params": path_params,
            "env": SimpleNamespace(
                method=alias, params=payload, target=target, model=model
            ),
        }
        ctx["response_serializer"] = lambda r: _serialize_output(
            model, alias, target, sp, r
        )
        phases = _get_phase_chains(model, alias)
        result = await _executor._invoke(
            request=request,
            db=db,
            phases=phases,
            ctx=ctx,
        )
        return result

    params = [
        inspect.Parameter(
            nv,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[str, Path(...)],
        )
        for nv in nested_vars
    ]
    params.extend(
        [
            inspect.Parameter(
                "item_id",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[Any, Path(...)],
            ),
            inspect.Parameter(
                "request",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Request,
            ),
            inspect.Parameter(
                "db",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[Any, Depends(db_dep)],
            ),
            inspect.Parameter(
                "body",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[body_annotation, body_default],
            ),
        ]
    )
    _endpoint.__signature__ = inspect.Signature(params)

    _endpoint.__name__ = f"rest_{model.__name__}_{alias}_member"
    _endpoint.__qualname__ = _endpoint.__name__
    _endpoint.__doc__ = f"REST member endpoint for {model.__name__}.{alias} ({target})"
    _endpoint.__annotations__["body"] = body_annotation
    return _endpoint


# ───────────────────────────────────────────────────────────────────────────────
# Router builder
# ───────────────────────────────────────────────────────────────────────────────


def _build_router(model: type, specs: Sequence[OpSpec]) -> Router:
    resource = _resource_name(model)

    # Router-level deps: extra deps only (transport-level; never part of runtime plan)
    extra_router_deps = _normalize_deps(
        getattr(model, AUTOAPI_REST_DEPENDENCIES_ATTR, None)
    )
    auth_dep = getattr(model, AUTOAPI_AUTH_DEP_ATTR, None)

    # Verbs explicitly allowed without auth
    allow_anon_attr = getattr(model, AUTOAPI_ALLOW_ANON_ATTR, None)
    allow_anon = set(
        allow_anon_attr() if callable(allow_anon_attr) else allow_anon_attr or []
    )

    router = Router(dependencies=extra_router_deps or None)

    pk_param = "item_id"
    db_dep = (
        getattr(model, AUTOAPI_GET_ASYNC_DB_ATTR, None)
        or getattr(model, AUTOAPI_GET_DB_ATTR, None)
        or _req_state_db
    )

    raw_nested = _nested_prefix(model) or ""
    nested_pref = re.sub(r"/{2,}", "/", raw_nested).rstrip("/") or ""
    nested_vars = re.findall(r"{(\w+)}", raw_nested)

    # If bulk_delete is present, drop clear to avoid route conflicts
    if any(sp.target == "bulk_delete" for sp in specs):
        specs = [sp for sp in specs if sp.target != "clear"]

    # Register collection-level bulk routes before member routes so static paths
    # like "/resource/bulk" aren't captured by dynamic member routes such as
    # "/resource/{item_id}". FastAPI matches routes in the order they are
    # added, so sorting here prevents "bulk" from being treated as an
    # identifier. Ensure the single-record ``create`` route is registered
    # before ``bulk_create`` so regular POSTs continue to behave as expected.
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

        # Drop parent identifiers from request models when using nested paths
        if nested_vars:
            schemas_root = getattr(model, "schemas", None)
            if schemas_root:
                alias_ns = getattr(schemas_root, sp.alias, None)
                if alias_ns:
                    in_model = getattr(alias_ns, "in_", None)
                    if (
                        in_model
                        and inspect.isclass(in_model)
                        and issubclass(in_model, BaseModel)
                    ):
                        target = in_model
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
                                target = inner
                        pruned = _strip_parent_fields(target, drop=set(nested_vars))
                        setattr(alias_ns, "in_", pruned)

        # Determine path and membership
        if nested_pref:
            suffix = sp.path_suffix or _default_path_suffix(sp) or ""
            if not suffix.startswith("/") and suffix:
                suffix = "/" + suffix
            base = nested_pref.rstrip("/")
            if not base.endswith(f"/{resource}"):
                base = f"{base}/{resource}"
            if sp.arity == "member" or sp.target in {
                "read",
                "update",
                "replace",
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
                        and not getattr(in_model, "__autoapi_optionalized__", False)
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
            )
        else:
            endpoint = _make_collection_endpoint(
                model,
                sp,
                resource=resource,
                db_dep=db_dep,
                nested_vars=nested_vars,
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

        route_kwargs = dict(
            path=path,
            endpoint=endpoint,
            methods=methods,
            name=f"{model.__name__}.{sp.alias}",
            summary=label,
            description=label,
            response_model=response_model,
            status_code=status_code,
            # IMPORTANT: only class name here; never table name
            tags=list(sp.tags or (model.__name__,)),
            responses=responses_meta,
        )
        if route_deps:
            route_kwargs["dependencies"] = route_deps
        if response_class is not None:
            route_kwargs["response_class"] = response_class

        secdeps: list[Any] = []
        if auth_dep and sp.alias not in allow_anon and sp.target not in allow_anon:
            secdeps.append(auth_dep)
        secdeps.extend(getattr(sp, "secdeps", ()))
        route_secdeps = _normalize_secdeps(secdeps)
        if route_secdeps:
            route_kwargs["dependencies"] = route_secdeps

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


# ───────────────────────────────────────────────────────────────────────────────
# Public API
# ───────────────────────────────────────────────────────────────────────────────


def build_router_and_attach(
    model: type, specs: Sequence[OpSpec], *, only_keys: Optional[Sequence[_Key]] = None
) -> None:
    """
    Build a Router for the model and attach it to `model.rest.router`.
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
