"""Shared interfaces for tigrbl.bindings.rest.

This module re-exports helper utilities split across smaller modules to keep the
import surface stable while easing maintenance.
"""

from __future__ import annotations
import logging

from pydantic import BaseModel

from .fastapi import (
    Body,
    Depends,
    HTTPException,
    Path,
    Query,
    Request,
    Response,
    Router,
    Security,
    _status,
)
from .helpers import (
    _Key,
    _coerce_parent_kw,
    _ensure_jsonable,
    _get_phase_chains,
    _pk_name,
    _pk_names,
    _req_state_db,
    _resource_name,
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
    _normalize_secdeps,
    _require_auth_header,
    _requires_auth_header,
    _path_for_spec,
    _request_model_for,
    _response_model_for,
    _status_for,
)
from ...config.constants import (
    TIGRBL_ALLOW_ANON_ATTR,
    TIGRBL_AUTH_CONTEXT_ATTR,
    TIGRBL_AUTH_DEP_ATTR,
    TIGRBL_GET_DB_ATTR,
    TIGRBL_REST_DEPENDENCIES_ATTR,
)
from ...op import OpSpec
from ...op.types import CANON, PHASES
from ...rest import _nested_prefix
from ...runtime import executor as _executor
from ...schema.builder import _strip_parent_fields

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/rest/common")

__all__ = [
    "Body",
    "Depends",
    "HTTPException",
    "Path",
    "Query",
    "Request",
    "Response",
    "Router",
    "Security",
    "_status",
    "BaseModel",
    "OpSpec",
    "CANON",
    "PHASES",
    "_executor",
    "TIGRBL_GET_DB_ATTR",
    "TIGRBL_AUTH_DEP_ATTR",
    "TIGRBL_REST_DEPENDENCIES_ATTR",
    "TIGRBL_ALLOW_ANON_ATTR",
    "TIGRBL_AUTH_CONTEXT_ATTR",
    "_nested_prefix",
    "_strip_parent_fields",
    "logger",
    "_Key",
    "_ensure_jsonable",
    "_req_state_db",
    "_resource_name",
    "_pk_name",
    "_pk_names",
    "_get_phase_chains",
    "_coerce_parent_kw",
    "_serialize_output",
    "_validate_body",
    "_validate_query",
    "_strip_optional",
    "_make_list_query_dep",
    "_optionalize_list_in_model",
    "_normalize_deps",
    "_normalize_secdeps",
    "_require_auth_header",
    "_requires_auth_header",
    "_status_for",
    "_RESPONSES_META",
    "_DEFAULT_METHODS",
    "_default_path_suffix",
    "_path_for_spec",
    "_response_model_for",
    "_request_model_for",
]
