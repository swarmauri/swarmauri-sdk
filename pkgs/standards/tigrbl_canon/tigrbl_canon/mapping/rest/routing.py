from __future__ import annotations
import logging

from types import SimpleNamespace
from typing import Any, Dict, Optional, Sequence, Tuple


from tigrbl_runtime.runtime.status.mappings import status as _status
from tigrbl_concrete._concrete.dependencies import Depends
from tigrbl_core._spec import OpSpec
from tigrbl_core.config.constants import CANON

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/mapping/rest/routing")


def _normalize_deps(deps: Optional[Sequence[Any]]) -> list[Any]:
    """Turn callables into Depends(...) unless already a dependency object."""
    if deps is None:
        return []

    if isinstance(deps, (str, bytes, bytearray)):
        normalized: tuple[Any, ...] = (deps,)
    else:
        try:
            normalized = tuple(deps)
        except TypeError:
            normalized = (deps,)

    if not normalized:
        return []

    out: list[Any] = []
    for d in normalized:
        is_dep_obj = getattr(d, "dependency", None) is not None
        out.append(d if is_dep_obj else Depends(d))
    return out


def _status_for(sp: OpSpec) -> int:
    if sp.status_code is not None:
        return sp.status_code
    target = sp.target
    if target == "create":
        return _status.HTTP_201_CREATED
    if target in ("delete", "clear"):
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
    "custom": ("POST",),
}


def _default_path_suffix(sp: OpSpec) -> str | None:
    if sp.target.startswith("bulk_"):
        return None

    # Canonical CRUD targets always keep their canonical route shape even when
    # declared through ``@op_ctx(alias=..., target=<canon>)``.
    if sp.target in CANON and sp.target != "custom":
        return None

    # Non-canonical/custom targets default to a dedicated alias suffix.
    return f"/{sp.alias}" if sp.alias else None


def _path_for_spec(
    model: type, sp: OpSpec, *, resource: str, pk_param: str = "item_id"
) -> Tuple[str, bool]:
    if sp.path_suffix is None:
        suffix = _default_path_suffix(sp) or ""
    else:
        suffix = sp.path_suffix or ""
    if suffix and not suffix.startswith("/"):
        suffix = "/" + suffix

    if sp.target == "create":
        return f"/{resource}{suffix}", False
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
    if sp.target == "delete":
        return None
    alias_ns = getattr(
        getattr(model, "schemas", None) or SimpleNamespace(), sp.alias, None
    )
    out_model = getattr(alias_ns, "out", None)
    if out_model is None:
        return None
    if sp.target == "list":
        try:
            return list[out_model]  # type: ignore[index]
        except Exception:
            return None
    return out_model


def _request_model_for(sp: OpSpec, model: type) -> Any | None:
    alias_ns = getattr(
        getattr(model, "schemas", None) or SimpleNamespace(), sp.alias, None
    )
    return getattr(alias_ns, "in_", None)
