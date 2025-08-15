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

from typing import Mapping, Tuple

from ..opspec.types import CANON  # canonical op registry (dict-like of targets)


# ───────────────────────────────────────────────────────────────────────────────
# Verbs / targets
# ───────────────────────────────────────────────────────────────────────────────

# Source of truth: `CANON` keys (strings like "create", "read", "bulk_update", ...)
ALL_VERBS: frozenset[str] = frozenset(
    str(k) for k in (CANON.keys() if hasattr(CANON, "keys") else CANON)
)  # type: ignore[arg-type]

# Bulk targets are those prefixed with "bulk_"
BULK_VERBS: frozenset[str] = frozenset(v for v in ALL_VERBS if v.startswith("bulk_"))

# Routable canonical (non-bulk) verbs; excludes the synthetic "custom"
ROUTING_VERBS: frozenset[str] = frozenset(
    v for v in ALL_VERBS if not v.startswith("bulk_") and v != "custom"
)


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

COL_LEVEL_CFGS: frozenset[str] = frozenset(
    {
        # legacy switches (still recognized)
        "no_create",  # legacy: exclude column on create
        "no_update",  # legacy: exclude column on update/replace
        # modern flags (kept in v3)
        "disable_on",  # iterable of verbs to disable this field on
        "write_only",  # omit in OUT/read schemas
        "read_only",  # omit from IN when True or when verb is in mapping
        "default_factory",  # callable to produce default Field value
        "examples",  # example values for OpenAPI/Pydantic
        "hybrid",  # opt-in for @hybrid_property fields
        "py_type",  # explicit Python type for hybrids/unknowns
    }
)


# ───────────────────────────────────────────────────────────────────────────────
# Model-level configuration attributes (looked up on the SQLAlchemy class)
# ───────────────────────────────────────────────────────────────────────────────

MODEL_LEVEL_CFGS: frozenset[str] = frozenset(
    {
        "__autoapi_request_extras__",  # request-only virtual fields per verb
        "__autoapi_response_extras__",  # response-only virtual fields per verb
        "__autoapi_ops__",  # declarative OpSpec list from decorators
        "__autoapi_verb_aliases__",  # optional verb alias map
        "__autoapi_verb_alias_policy__",  # alias policy override
        "__autoapi_nested_paths__",  # nested path callback (optional)
        "__autoapi_hooks__",  # static hook map attached to model
        "__autoapi_api_hooks__",  # API-level hooks merged onto model
        "__autoapi_imperative_hooks__",  # imperative hook map attached to model
        "__autoapi_auth_dep__",  # FastAPI dependency for auth
        "__autoapi_authorize__",  # authorization callback
        "__autoapi_get_db__",  # sync DB session getter
        "__autoapi_get_async_db__",  # async DB session getter
        "__autoapi_rest_dependencies__",  # extra REST dependencies
        "__autoapi_rpc_dependencies__",  # extra RPC dependencies
        "__autoapi_registry_listener__",  # registry listener callback
        "__autoapi_owner_policy__",  # owner policy for Ownable
        "__autoapi_tenant_policy__",  # tenant policy for TenantBound
        "__autoapi_defaults_mode__",  # default op config mode
        "__autoapi_defaults_include__",  # default op config include
        "__autoapi_defaults_exclude__",  # default op config exclude
        "__resource__",  # resource name override for REST
    }
)


# ───────────────────────────────────────────────────────────────────────────────
# Internal attribute names (attached via ``getattr``/``setattr``)
# ───────────────────────────────────────────────────────────────────────────────

API_HOOKS_ATTR = "__autoapi_api_hooks__"
AUTH_DEP_ATTR = "__autoapi_auth_dep__"
AUTHORIZE_ATTR = "__autoapi_authorize__"
GET_DB_ATTR = "__autoapi_get_db__"
GET_ASYNC_DB_ATTR = "__autoapi_get_async_db__"
REST_DEPS_ATTR = "__autoapi_rest_dependencies__"
RPC_DEPS_ATTR = "__autoapi_rpc_dependencies__"
HOOKS_ATTR = "__autoapi_hooks__"
IMPERATIVE_HOOKS_ATTR = "__autoapi_imperative_hooks__"
REGISTRY_LISTENER_ATTR = "__autoapi_registry_listener__"
TX_MODELS_ATTR = "__autoapi_tx_models__"
OWNER_POLICY_ATTR = "__autoapi_owner_policy__"
TENANT_POLICY_ATTR = "__autoapi_tenant_policy__"
CUSTOM_OP_ATTR = "__autoapi_custom_op__"
OPS_ATTR = "__autoapi_ops__"
VERB_ALIASES_ATTR = "__autoapi_verb_aliases__"
VERB_ALIAS_POLICY_ATTR = "__autoapi_verb_alias_policy__"
REQUEST_EXTRAS_ATTR = "__autoapi_request_extras__"
RESPONSE_EXTRAS_ATTR = "__autoapi_response_extras__"
DEFAULTS_MODE_ATTR = "__autoapi_defaults_mode__"
DEFAULTS_INCLUDE_ATTR = "__autoapi_defaults_include__"
DEFAULTS_EXCLUDE_ATTR = "__autoapi_defaults_exclude__"
NESTED_PATHS_ATTR = "__autoapi_nested_paths__"


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
CTX_RPC_ID_KEY = "rpc_id"  # used by the JSON-RPC dispatcher
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
    "API_HOOKS_ATTR",
    "AUTH_DEP_ATTR",
    "AUTHORIZE_ATTR",
    "GET_DB_ATTR",
    "GET_ASYNC_DB_ATTR",
    "REST_DEPS_ATTR",
    "RPC_DEPS_ATTR",
    "HOOKS_ATTR",
    "IMPERATIVE_HOOKS_ATTR",
    "REGISTRY_LISTENER_ATTR",
    "TX_MODELS_ATTR",
    "OWNER_POLICY_ATTR",
    "TENANT_POLICY_ATTR",
    "CUSTOM_OP_ATTR",
    "OPS_ATTR",
    "VERB_ALIASES_ATTR",
    "VERB_ALIAS_POLICY_ATTR",
    "REQUEST_EXTRAS_ATTR",
    "RESPONSE_EXTRAS_ATTR",
    "DEFAULTS_MODE_ATTR",
    "DEFAULTS_INCLUDE_ATTR",
    "DEFAULTS_EXCLUDE_ATTR",
    "NESTED_PATHS_ATTR",
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
