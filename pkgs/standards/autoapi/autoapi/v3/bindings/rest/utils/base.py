"""Core utilities and FastAPI shims for REST bindings."""

from __future__ import annotations

import inspect
import logging
from types import SimpleNamespace
from typing import Any, Awaitable, Callable, Dict, Mapping, Sequence

from ...ops import OpSpec
from ...ops.types import PHASES

try:  # pragma: no cover - FastAPI may be unavailable
    from ...types import (
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

    def Path(default=None, **kw):  # type: ignore
        return default

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


from pydantic import BaseModel

# Prefer Kernel phase-chains if available
try:  # pragma: no cover - optional kernel
    from ...runtime.kernel import build_phase_chains as _kernel_build_phase_chains  # type: ignore
except Exception:  # pragma: no cover - kernel unavailable
    _kernel_build_phase_chains = None  # type: ignore


logger = logging.getLogger("autoapi.v3.bindings.rest")


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


def _resource_name(model: type) -> str:
    """HTTP resource segment for paths/tags."""
    override = getattr(model, "__resource__", None)
    return override or model.__name__.lower()


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


def _pk_names(model: type) -> set[str]:
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
    """Prefer building via runtime Kernel; fallback to model.hooks chains."""
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
    """Serialize a result to an output schema if one exists."""
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


__all__ = [
    "Router",
    "Request",
    "Body",
    "Depends",
    "HTTPException",
    "Response",
    "Path",
    "Security",
    "Query",
    "_status",
    "logger",
    "_ensure_jsonable",
    "_req_state_db",
    "_resource_name",
    "_pk_name",
    "_pk_names",
    "_get_phase_chains",
    "_serialize_output",
]
