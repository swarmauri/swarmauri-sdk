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

# Well-known attribute names injected or inspected on ORM models
AUTOAPI_REQUEST_EXTRAS_ATTR = (
    "__autoapi_request_extras__"  # request-only virtual fields per verb
)
AUTOAPI_RESPONSE_EXTRAS_ATTR = (
    "__autoapi_response_extras__"  # response-only virtual fields per verb
)
AUTOAPI_OPS_ATTR = "__autoapi_ops__"  # declarative OpSpec list from decorators
AUTOAPI_VERB_ALIASES_ATTR = "__autoapi_verb_aliases__"  # optional verb alias map
AUTOAPI_VERB_ALIAS_POLICY_ATTR = (
    "__autoapi_verb_alias_policy__"  # alias policy override
)
AUTOAPI_NESTED_PATHS_ATTR = (
    "__autoapi_nested_paths__"  # nested path callback (optional)
)
AUTOAPI_API_HOOKS_ATTR = "__autoapi_api_hooks__"  # API-level hooks map
AUTOAPI_HOOKS_ATTR = "__autoapi_hooks__"  # model-level hooks map
AUTOAPI_REGISTRY_LISTENER_ATTR = (
    "__autoapi_registry_listener__"  # ops registry listener
)
AUTOAPI_GET_DB_ATTR = "__autoapi_get_db__"  # sync DB dependency
AUTOAPI_GET_ASYNC_DB_ATTR = "__autoapi_get_async_db__"  # async DB dependency
AUTOAPI_AUTH_DEP_ATTR = "__autoapi_auth_dep__"  # auth dependency
AUTOAPI_AUTHORIZE_ATTR = "__autoapi_authorize__"  # authorization callable
AUTOAPI_REST_DEPENDENCIES_ATTR = "__autoapi_rest_dependencies__"  # extra REST deps
AUTOAPI_RPC_DEPENDENCIES_ATTR = "__autoapi_rpc_dependencies__"  # extra RPC deps
AUTOAPI_OWNER_POLICY_ATTR = "__autoapi_owner_policy__"  # ownership policy override
AUTOAPI_TENANT_POLICY_ATTR = "__autoapi_tenant_policy__"  # tenancy policy override
AUTOAPI_ALLOW_ANON_ATTR = "__autoapi_allow_anon__"  # verbs callable without auth
AUTOAPI_DEFAULTS_MODE_ATTR = "__autoapi_defaults_mode__"  # canonical verb wiring policy
AUTOAPI_DEFAULTS_INCLUDE_ATTR = "__autoapi_defaults_include__"  # verbs to force include
AUTOAPI_DEFAULTS_EXCLUDE_ATTR = "__autoapi_defaults_exclude__"  # verbs to force exclude

# Aggregate of recognized model-level config attributes
MODEL_LEVEL_CFGS: frozenset[str] = frozenset(
    {
        AUTOAPI_REQUEST_EXTRAS_ATTR,
        AUTOAPI_RESPONSE_EXTRAS_ATTR,
        AUTOAPI_OPS_ATTR,
        AUTOAPI_VERB_ALIASES_ATTR,
        AUTOAPI_VERB_ALIAS_POLICY_ATTR,
        AUTOAPI_NESTED_PATHS_ATTR,
        AUTOAPI_API_HOOKS_ATTR,
        AUTOAPI_HOOKS_ATTR,
        AUTOAPI_REGISTRY_LISTENER_ATTR,
        AUTOAPI_GET_DB_ATTR,
        AUTOAPI_GET_ASYNC_DB_ATTR,
        AUTOAPI_AUTH_DEP_ATTR,
        AUTOAPI_AUTHORIZE_ATTR,
        AUTOAPI_REST_DEPENDENCIES_ATTR,
        AUTOAPI_RPC_DEPENDENCIES_ATTR,
        AUTOAPI_OWNER_POLICY_ATTR,
        AUTOAPI_TENANT_POLICY_ATTR,
        AUTOAPI_ALLOW_ANON_ATTR,
        AUTOAPI_DEFAULTS_MODE_ATTR,
        AUTOAPI_DEFAULTS_INCLUDE_ATTR,
        AUTOAPI_DEFAULTS_EXCLUDE_ATTR,
        "__resource__",  # resource name override for REST
    }
)

# Other internal attribute names
AUTOAPI_CUSTOM_OP_ATTR = "__autoapi_custom_op__"  # marker for custom opspec
AUTOAPI_TX_MODELS_ATTR = "__autoapi_tx_models__"  # transactional model cache


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
AUTOAPI_AUTH_CONTEXT_ATTR = "__autoapi_auth_context__"


__all__ = [
    "ALL_VERBS",
    "BULK_VERBS",
    "ROUTING_VERBS",
    "DEFAULT_HTTP_METHODS",
    "COL_LEVEL_CFGS",
    "MODEL_LEVEL_CFGS",
    "AUTOAPI_REQUEST_EXTRAS_ATTR",
    "AUTOAPI_RESPONSE_EXTRAS_ATTR",
    "AUTOAPI_OPS_ATTR",
    "AUTOAPI_VERB_ALIASES_ATTR",
    "AUTOAPI_VERB_ALIAS_POLICY_ATTR",
    "AUTOAPI_NESTED_PATHS_ATTR",
    "AUTOAPI_API_HOOKS_ATTR",
    "AUTOAPI_HOOKS_ATTR",
    "AUTOAPI_REGISTRY_LISTENER_ATTR",
    "AUTOAPI_GET_DB_ATTR",
    "AUTOAPI_GET_ASYNC_DB_ATTR",
    "AUTOAPI_AUTH_DEP_ATTR",
    "AUTOAPI_AUTHORIZE_ATTR",
    "AUTOAPI_REST_DEPENDENCIES_ATTR",
    "AUTOAPI_RPC_DEPENDENCIES_ATTR",
    "AUTOAPI_OWNER_POLICY_ATTR",
    "AUTOAPI_TENANT_POLICY_ATTR",
    "AUTOAPI_ALLOW_ANON_ATTR",
    "AUTOAPI_DEFAULTS_MODE_ATTR",
    "AUTOAPI_DEFAULTS_INCLUDE_ATTR",
    "AUTOAPI_DEFAULTS_EXCLUDE_ATTR",
    "AUTOAPI_CUSTOM_OP_ATTR",
    "AUTOAPI_TX_MODELS_ATTR",
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
    "AUTOAPI_AUTH_CONTEXT_ATTR",
]
