# autoapi/v3/config/constants.py
"""
AutoAPI v3 – Configuration constants

Centralizes “well-known” names and defaults used across v3. These are
pure-Python constants; there is no runtime coupling to any web framework.

Highlights
----------
• Verbs/targets are *derived* from the v3 OpSpec canon so they always stay in sync.
• Default HTTP method mapping for REST bindings lives here (used by bindings.rest).
• Column / model config keys document the names we look for in SQLAlchemy
  Column.info["autoapi"] and on model classes.

Nothing in this module performs I/O.
"""

from __future__ import annotations

from typing import Dict, Mapping, Tuple

from ..opspec.types import CANON  # canonical op registry (dict-like of targets)


# ───────────────────────────────────────────────────────────────────────────────
# Verbs / targets
# ───────────────────────────────────────────────────────────────────────────────

# Source of truth: `CANON` keys (strings like "create", "read", "bulk_update", ...)
ALL_VERBS: frozenset[str] = frozenset(str(k) for k in (CANON.keys() if hasattr(CANON, "keys") else CANON))  # type: ignore[arg-type]

# Bulk targets are those prefixed with "bulk_"
BULK_VERBS: frozenset[str] = frozenset(v for v in ALL_VERBS if v.startswith("bulk_"))

# Routable canonical (non-bulk) verbs; excludes the synthetic "custom"
ROUTING_VERBS: frozenset[str] = frozenset(v for v in ALL_VERBS if not v.startswith("bulk_") and v != "custom")


# ───────────────────────────────────────────────────────────────────────────────
# Default HTTP methods per target (bindings.rest uses this unless overridden)
# ───────────────────────────────────────────────────────────────────────────────

DEFAULT_HTTP_METHODS: Mapping[str, Tuple[str, ...]] = {
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
    "custom": ("POST",),
}


# ───────────────────────────────────────────────────────────────────────────────
# Column-level configuration keys (Column.info["autoapi"])
#   See: v3 schema builder & v3 schema.info check(meta, attr, model)
# ───────────────────────────────────────────────────────────────────────────────

COL_LEVEL_CFGS: frozenset[str] = frozenset({
    # legacy switches (still recognized)
    "no_create",            # legacy: exclude column on create
    "no_update",            # legacy: exclude column on update/replace
    # modern flags (kept in v3)
    "disable_on",           # iterable of verbs to disable this field on
    "write_only",           # omit in OUT/read schemas
    "read_only",            # omit from IN when True or when verb is in mapping
    "default_factory",      # callable to produce default Field value
    "examples",             # example values for OpenAPI/Pydantic
    "hybrid",               # opt-in for @hybrid_property fields
    "py_type",              # explicit Python type for hybrids/unknowns
})


# ───────────────────────────────────────────────────────────────────────────────
# Model-level configuration attributes (looked up on the SQLAlchemy class)
# ───────────────────────────────────────────────────────────────────────────────

MODEL_LEVEL_CFGS: frozenset[str] = frozenset({
    "__autoapi_request_extras__",   # request-only virtual fields per verb
    "__autoapi_response_extras__",  # response-only virtual fields per verb
    "__autoapi_ops__",              # declarative OpSpec list from decorators
    "__autoapi_verb_aliases__",     # optional verb alias map
    "__autoapi_verb_alias_policy__",# alias policy override
    "__autoapi_nested_paths__",     # nested path callback (optional)
    "__resource__",                 # resource name override for REST
})


# ───────────────────────────────────────────────────────────────────────────────
# Common context keys used throughout runtime/bindings (non-normative)
# ───────────────────────────────────────────────────────────────────────────────

# These string constants are *conventional* keys you may put into ctx, not
# enforced by AutoAPI. They’re listed here for discoverability.
CTX_REQUEST_KEY = "request"
CTX_DB_KEY = "db"
CTX_PAYLOAD_KEY = "payload"
CTX_PATH_PARAMS_KEY = "path_params"
CTX_ENV_KEY = "env"
CTX_RPC_ID_KEY = "rpc_id"                    # used by the JSON-RPC dispatcher
CTX_SKIP_PERSIST_FLAG = "__autoapi_skip_persist__"  # set by ephemeral ops

# Optional auth/multitenancy keys that middlewares may populate for hooks to read
CTX_USER_ID_KEY = "user_id"
CTX_TENANT_ID_KEY = "tenant_id"
CTX_AUTH_KEY = "auth"


__all__ = [
    "ALL_VERBS",
    "BULK_VERBS",
    "ROUTING_VERBS",
    "DEFAULT_HTTP_METHODS",
    "COL_LEVEL_CFGS",
    "MODEL_LEVEL_CFGS",
    "CTX_REQUEST_KEY",
    "CTX_DB_KEY",
    "CTX_PAYLOAD_KEY",
    "CTX_PATH_PARAMS_KEY",
    "CTX_ENV_KEY",
    "CTX_RPC_ID_KEY",
    "CTX_SKIP_PERSIST_FLAG",
    "CTX_USER_ID_KEY",
    "CTX_TENANT_ID_KEY",
    "CTX_AUTH_KEY",
]
