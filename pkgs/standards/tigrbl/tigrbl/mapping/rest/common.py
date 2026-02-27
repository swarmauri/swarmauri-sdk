"""Shared interfaces for tigrbl.mapping.rest.

This module re-exports helper utilities split across smaller modules to keep the
import surface stable while easing maintenance.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel

from .helpers import (
    _Key,
    _coerce_parent_kw,
    _ensure_jsonable,
    _get_phase_chains,
    _pk_name,
    _pk_names,
    _req_state_db,
)
from .io import (
    _make_list_query_dep,
    _optionalize_list_in_model,
    _serialize_output,
    _strip_optional,
    _validate_body,
    _validate_query,
)
from .routing import (
    _DEFAULT_METHODS,
    _RESPONSES_META,
    _default_path_suffix,
    _normalize_deps,
    _path_for_spec,
    _request_model_for,
    _response_model_for,
    _status_for,
)
from ..._concrete._request import Request
from ..._concrete._response import Response
from ..._concrete._router import Router
from ...config.constants import (
    TIGRBL_ALLOW_ANON_ATTR,
    TIGRBL_AUTH_CONTEXT_ATTR,
    TIGRBL_AUTH_DEP_ATTR,
    TIGRBL_GET_DB_ATTR,
    TIGRBL_REST_DEPENDENCIES_ATTR,
)
from ...core.crud.params import Body, Path
from ...op import OpSpec
from ...op.types import CANON
from ...rest import _nested_prefix
from ...runtime import executor as _executor
from ...runtime.status.exceptions import HTTPException
from ...runtime.status.mappings import status as _status
from ...schema.builder import _strip_parent_fields
from ...security.dependencies import Depends

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/mapping/rest/common")


def _is_http_response(obj: Any) -> bool:
    """Best-effort response detection across Tigrbl and Starlette response types."""
    if isinstance(obj, Response):
        return True
    return (
        hasattr(obj, "status_code")
        and hasattr(obj, "headers")
        and (
            hasattr(obj, "body")
            or hasattr(obj, "body_iterator")
            or hasattr(obj, "render")
        )
    )


__all__ = [
    "BaseModel",
    "Body",
    "CANON",
    "Depends",
    "HTTPException",
    "OpSpec",
    "Path",
    "Request",
    "Response",
    "Router",
    "TIGRBL_ALLOW_ANON_ATTR",
    "TIGRBL_AUTH_CONTEXT_ATTR",
    "TIGRBL_AUTH_DEP_ATTR",
    "TIGRBL_GET_DB_ATTR",
    "TIGRBL_REST_DEPENDENCIES_ATTR",
    "_DEFAULT_METHODS",
    "_Key",
    "_RESPONSES_META",
    "_coerce_parent_kw",
    "_default_path_suffix",
    "_ensure_jsonable",
    "_executor",
    "_get_phase_chains",
    "_is_http_response",
    "_make_list_query_dep",
    "_nested_prefix",
    "_normalize_deps",
    "_optionalize_list_in_model",
    "_path_for_spec",
    "_pk_name",
    "_pk_names",
    "_req_state_db",
    "_request_model_for",
    "_response_model_for",
    "_serialize_output",
    "_status",
    "_status_for",
    "_strip_optional",
    "_strip_parent_fields",
    "_validate_body",
    "_validate_query",
]
