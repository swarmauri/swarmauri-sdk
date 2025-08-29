"""
cfgs.py

Collect AutoAPI configuration hooks by category.

This module groups the special Column.info keys, class attributes, and
runtime configuration names recognized by AutoAPI into high level
categories for easier reference.
"""

# Column-level configuration keys found in ``Column.info`` or ``info["autoapi"]``
COL_LEVEL_CFGS: set[str] = {
    "no_create",
    "no_update",
    "hybrid",
    "disable_on",
    "write_only",
    "read_only",
    "default_factory",
    "examples",
    "py_type",
}

# Table-level configuration attributes on ORM classes
TAB_LEVEL_CFGS: set[str] = {
    "__autoapi_request_extras__",
    "__autoapi_response_extras__",
    "__autoapi_register_hooks__",
    "__autoapi_owner_policy__",
    "__autoapi_tenant_policy__",
    "__autoapi_nested_paths__",
    "__autoapi_allow_anon__",
    "__autoapi_verb_aliases__",
    "__autoapi_verb_alias_policy__",
    "__autoapi_security_deps__",
}

# Routing configuration attributes
ROUTING_CFGS: set[str] = {
    "__autoapi_nested_paths__",
    "__autoapi_verb_aliases__",
    "__autoapi_verb_alias_policy__",
}

# Persistence customization hooks
PERSISTENCE_CFGS: set[str] = {
    "__autoapi_register_hooks__",
}

# Runtime context keys
AUTH_CONTEXT_KEY = "__autoapi_auth_context__"
INJECTED_FIELDS_KEY = "__autoapi_injected_fields__"
TENANT_ID_KEY = "tenant_id"
USER_ID_KEY = "user_id"

# Principal-related configuration
PRINCIPAL_CFGS: set[str] = {
    "__autoapi_tenant_policy__",
    "__autoapi_owner_policy__",
    AUTH_CONTEXT_KEY,
}

# Security related configuration
SECURITY_CFGS: set[str] = {
    "authn",
    AUTH_CONTEXT_KEY,
    INJECTED_FIELDS_KEY,
    "authorize",
}

# Dependency related hooks
DEPS_CFGS: set[str] = {
    "get_db",
    "get_async_db",
}

# Routing verbs
ROUTING_VERBS: set[str] = {
    "create",
    "read",
    "update",
    "delete",
    "list",
    "clear",
    "replace",
}

# Bulk operation verbs
BULK_VERBS: set[str] = {
    "bulk_create",
    "bulk_update",
    "bulk_replace",
    "bulk_delete",
}

# All supported verbs
ALL_VERBS: set[str] = ROUTING_VERBS | BULK_VERBS
