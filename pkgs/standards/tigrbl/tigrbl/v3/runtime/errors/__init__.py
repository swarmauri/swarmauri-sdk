from __future__ import annotations

from .utils import HTTPException, status
from .mappings import (
    HTTP_ERROR_MESSAGES,
    ERROR_MESSAGES,
    _HTTP_TO_RPC,
    _RPC_TO_HTTP,
)
from .converters import (
    http_exc_to_rpc,
    rpc_error_to_http,
    _http_exc_to_rpc,
    _rpc_error_to_http,
    create_standardized_error,
    create_standardized_error_from_status,
    to_rpc_error_payload,
)
from .exceptions import (
    TigrblError,
    PlanningError,
    LabelError,
    ConfigError,
    SystemStepError,
    ValidationError,
    TransformError,
    DeriveError,
    KernelAbort,
    coerce_runtime_error,
    raise_for_in_errors,
)

__all__ = [
    "HTTPException",
    "status",
    # maps & messages
    "HTTP_ERROR_MESSAGES",
    "ERROR_MESSAGES",
    "_HTTP_TO_RPC",
    "_RPC_TO_HTTP",
    # conversions
    "http_exc_to_rpc",
    "rpc_error_to_http",
    "_http_exc_to_rpc",
    "_rpc_error_to_http",
    "create_standardized_error",
    "create_standardized_error_from_status",
    "to_rpc_error_payload",
    # typed errors + helpers
    "TigrblError",
    "PlanningError",
    "LabelError",
    "ConfigError",
    "SystemStepError",
    "ValidationError",
    "TransformError",
    "DeriveError",
    "KernelAbort",
    "coerce_runtime_error",
    "raise_for_in_errors",
]
