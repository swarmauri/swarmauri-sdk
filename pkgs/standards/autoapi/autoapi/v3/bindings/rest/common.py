# Shared helpers for autoapi.v3.bindings.rest
from __future__ import annotations

import inspect
import logging
import typing as _typing
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

from typing import get_origin as _get_origin, get_args as _get_args
from ...op.types import CANON

try:
    from ...types import (
        Router,
        Request,
        Body,
        Depends,
        HTTPException,
        Response,
        Path,  # noqa: F401
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

from ...op import OpSpec
from ...op.types import PHASES
from ...runtime import executor as _executor  # noqa: F401  # expects _invoke(request, db, phases, ctx)

# Prefer Kernel phase-chains if available
try:
    from ...runtime.kernel import build_phase_chains as _kernel_build_phase_chains  # type: ignore
except Exception:  # pragma: no cover
    _kernel_build_phase_chains = None  # type: ignore

from ...config.constants import (  # noqa: F401
    AUTOAPI_GET_DB_ATTR,
    AUTOAPI_AUTH_DEP_ATTR,
    AUTOAPI_REST_DEPENDENCIES_ATTR,
    AUTOAPI_ALLOW_ANON_ATTR,
    AUTOAPI_AUTH_CONTEXT_ATTR,
)
from ...rest import _nested_prefix  # noqa: F401
from ...schema.builder import _strip_parent_fields  # noqa: F401

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

    from ...types import Response as _Response  # local import to avoid cycles

    if isinstance(result, _Response):
        return result

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
    if sp.alias != sp.target and (
        sp.target in {"create", "custom"} or sp.target not in CANON
    ):
        return f"/{sp.alias}"
    return None


def _path_for_spec(
    model: type, sp: OpSpec, *, resource: str, pk_param: str = "item_id"
) -> Tuple[str, bool]:
    """
    Return (path, is_member). We use a generic {item_id} placeholder for all member ops
    and remap it to the model's real PK name inside ``ctx.path_params``.
    """
    if sp.path_suffix is None:
        suffix = _default_path_suffix(sp) or ""
    else:
        suffix = sp.path_suffix or ""
    if suffix and not suffix.startswith("/"):
        suffix = "/" + suffix

    if sp.arity == "member" or sp.target in {
        "read",
        "update",
        "replace",
        "merge",
        "delete",
    }:
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
