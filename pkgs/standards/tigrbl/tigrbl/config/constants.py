# tigrbl/v3/config/constants.py
"""
Tigrbl v3 – Configuration constants

Centralizes “well-known” names and defaults used across v3. These are
pure-Python constants; there is no runtime coupling to any web framework.

Highlights
----------
• Verbs/targets are *derived* from the v3 OpSpec canon so they always stay in sync.
• Default HTTP method mapping for REST bindings lives here (used by bindings.rest).
• Model config keys document the names we look for on SQLAlchemy classes.

Nothing in this module performs I/O.
"""

from __future__ import annotations

from typing import Mapping, Tuple
import re

# NOTE: importing CANON from ``ops.types`` introduces a circular dependency
# because that module transitively imports this one via ``hook``. To keep the
# constant values in sync without triggering the circular import at import time,
# we inline the canonical verb tuple here. This tuple **must** match
# ``tigrbl.op.types.CANON``.
CANON: Tuple[str, ...] = (
    "create",
    "read",
    "update",
    "replace",
    "merge",
    "delete",
    "list",
    "clear",
    "bulk_create",
    "bulk_update",
    "bulk_replace",
    "bulk_merge",
    "bulk_delete",
    "custom",
)


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
# Model-level configuration attributes (looked up on the SQLAlchemy class)
# ───────────────────────────────────────────────────────────────────────────────

# Well-known attribute names injected or inspected on ORM models
TIGRBL_REQUEST_EXTRAS_ATTR = (
    "__tigrbl_request_extras__"  # request-only virtual fields per verb
)
TIGRBL_RESPONSE_EXTRAS_ATTR = (
    "__tigrbl_response_extras__"  # response-only virtual fields per verb
)
TIGRBL_OPS_ATTR = "__tigrbl_ops__"  # declarative OpSpec list from decorators
TIGRBL_VERB_ALIASES_ATTR = "__tigrbl_verb_aliases__"  # optional verb alias map
TIGRBL_VERB_ALIAS_POLICY_ATTR = "__tigrbl_verb_alias_policy__"  # alias policy override
TIGRBL_NESTED_PATHS_ATTR = "__tigrbl_nested_paths__"  # nested path callback (optional)
TIGRBL_API_HOOKS_ATTR = "__tigrbl_api_hooks__"  # API-level hooks map
TIGRBL_HOOKS_ATTR = "__tigrbl_hooks__"  # model-level hooks map
TIGRBL_REGISTRY_LISTENER_ATTR = "__tigrbl_registry_listener__"  # ops registry listener
TIGRBL_GET_DB_ATTR = "__tigrbl_get_db__"  # DB dependency
TIGRBL_AUTH_DEP_ATTR = "__tigrbl_auth_dep__"  # auth dependency
TIGRBL_AUTHORIZE_ATTR = "__tigrbl_authorize__"  # authorization callable
TIGRBL_REST_DEPENDENCIES_ATTR = "__tigrbl_rest_dependencies__"  # extra REST deps
TIGRBL_RPC_DEPENDENCIES_ATTR = "__tigrbl_rpc_dependencies__"  # extra RPC deps
TIGRBL_OWNER_POLICY_ATTR = "__tigrbl_owner_policy__"  # ownership policy override
TIGRBL_TENANT_POLICY_ATTR = "__tigrbl_tenant_policy__"  # tenancy policy override
TIGRBL_ALLOW_ANON_ATTR = "__tigrbl_allow_anon__"  # verbs callable without auth
TIGRBL_DEFAULTS_MODE_ATTR = "__tigrbl_defaults_mode__"  # canonical verb wiring policy
TIGRBL_DEFAULTS_INCLUDE_ATTR = "__tigrbl_defaults_include__"  # verbs to force include
TIGRBL_DEFAULTS_EXCLUDE_ATTR = "__tigrbl_defaults_exclude__"  # verbs to force exclude
TIGRBL_SCHEMA_DECLS_ATTR = "__tigrbl_schema_decls__"  # declared schemas map

# Aggregate of recognized model-level config attributes
MODEL_LEVEL_CFGS: frozenset[str] = frozenset(
    {
        TIGRBL_REQUEST_EXTRAS_ATTR,
        TIGRBL_RESPONSE_EXTRAS_ATTR,
        TIGRBL_OPS_ATTR,
        TIGRBL_VERB_ALIASES_ATTR,
        TIGRBL_VERB_ALIAS_POLICY_ATTR,
        TIGRBL_NESTED_PATHS_ATTR,
        TIGRBL_API_HOOKS_ATTR,
        TIGRBL_HOOKS_ATTR,
        TIGRBL_REGISTRY_LISTENER_ATTR,
        TIGRBL_GET_DB_ATTR,
        TIGRBL_AUTH_DEP_ATTR,
        TIGRBL_AUTHORIZE_ATTR,
        TIGRBL_REST_DEPENDENCIES_ATTR,
        TIGRBL_RPC_DEPENDENCIES_ATTR,
        TIGRBL_OWNER_POLICY_ATTR,
        TIGRBL_TENANT_POLICY_ATTR,
        TIGRBL_ALLOW_ANON_ATTR,
        TIGRBL_DEFAULTS_MODE_ATTR,
        TIGRBL_DEFAULTS_INCLUDE_ATTR,
        TIGRBL_DEFAULTS_EXCLUDE_ATTR,
        TIGRBL_SCHEMA_DECLS_ATTR,
        "__resource__",  # resource name override for REST
    }
)

# Other internal attribute names
TIGRBL_CUSTOM_OP_ATTR = "__tigrbl_custom_op__"  # marker for custom op
HOOK_DECLS_ATTR = "__tigrbl_hook_decls__"  # per-function hook declarations

# ───────────────────────────────────────────────────────────────────────────────
# ‼ Everything is natively transactional now
# ‼ We will not support transactionals as a custom type or obj moving forward.
# ‼ Support is not guaranteed.
# ───────────────────────────────────────────────────────────────────────────────
TIGRBL_TX_MODELS_ATTR = "__tigrbl_tx_models__"  # transactional model cache


# ───────────────────────────────────────────────────────────────────────────────
# Common context keys used throughout runtime/bindings (non-normative)
# ───────────────────────────────────────────────────────────────────────────────

# These string constants are *conventional* keys you may put into ctx, not
# enforced by Tigrbl. They’re listed here for discoverability.
CTX_REQUEST_KEY = "request"
CTX_DB_KEY = "db"
CTX_PAYLOAD_KEY = "payload"
CTX_PATH_PARAMS_KEY = "path_params"
CTX_ENV_KEY = "env"
CTX_RPC_ID_KEY = "rpc_id"  # used by the JSON-RPC dispatcher
CTX_SKIP_PERSIST_FLAG = "__tigrbl_skip_persist__"  # set by ephemeral ops

# Optional auth/multitenancy keys that middlewares may populate for hooks to read
CTX_USER_ID_KEY = "user_id"
CTX_TENANT_ID_KEY = "tenant_id"
CTX_AUTH_KEY = "auth"

# Request.state attribute that carries auth context (tenant/user ids)
TIGRBL_AUTH_CONTEXT_ATTR = "__tigrbl_auth_context__"


# Regex for safe SQL identifiers
__SAFE_IDENT__ = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

__all__ = [
    "ALL_VERBS",
    "BULK_VERBS",
    "ROUTING_VERBS",
    "DEFAULT_HTTP_METHODS",
    "MODEL_LEVEL_CFGS",
    "TIGRBL_REQUEST_EXTRAS_ATTR",
    "TIGRBL_RESPONSE_EXTRAS_ATTR",
    "TIGRBL_OPS_ATTR",
    "TIGRBL_VERB_ALIASES_ATTR",
    "TIGRBL_VERB_ALIAS_POLICY_ATTR",
    "TIGRBL_NESTED_PATHS_ATTR",
    "TIGRBL_API_HOOKS_ATTR",
    "TIGRBL_HOOKS_ATTR",
    "TIGRBL_REGISTRY_LISTENER_ATTR",
    "TIGRBL_GET_DB_ATTR",
    "TIGRBL_AUTH_DEP_ATTR",
    "TIGRBL_AUTHORIZE_ATTR",
    "TIGRBL_REST_DEPENDENCIES_ATTR",
    "TIGRBL_RPC_DEPENDENCIES_ATTR",
    "TIGRBL_OWNER_POLICY_ATTR",
    "TIGRBL_TENANT_POLICY_ATTR",
    "TIGRBL_ALLOW_ANON_ATTR",
    "TIGRBL_DEFAULTS_MODE_ATTR",
    "TIGRBL_DEFAULTS_INCLUDE_ATTR",
    "TIGRBL_DEFAULTS_EXCLUDE_ATTR",
    "TIGRBL_SCHEMA_DECLS_ATTR",
    "TIGRBL_CUSTOM_OP_ATTR",
    "HOOK_DECLS_ATTR",
    "TIGRBL_TX_MODELS_ATTR",
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
    "TIGRBL_AUTH_CONTEXT_ATTR",
    "__SAFE_IDENT__",
]
