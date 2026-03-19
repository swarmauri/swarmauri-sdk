"""Canonical decorators package for Tigrbl."""

from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORTS = {
    # op
    "AliasDecl": "tigrbl_concrete._decorators.op",
    "alias": "tigrbl_concrete._decorators.op",
    "alias_ctx": "tigrbl_concrete._decorators.op",
    "op_alias": "tigrbl_concrete._decorators.op",
    "op_ctx": "tigrbl_concrete._decorators.op",
    # hook
    "HOOK_DECLS_ATTR": "tigrbl_concrete._decorators.hook",
    "hook_ctx": "tigrbl_concrete._decorators.hook",
    # engine/schema/session
    "engine_ctx": "tigrbl_concrete._decorators.engine",
    "schema_ctx": "tigrbl_concrete._decorators.schema",
    "session_ctx": "tigrbl_concrete._decorators.session",
    "read_only_session": "tigrbl_concrete._decorators.session",
    # middleware
    "MiddlewareConfig": "tigrbl_concrete._decorators.middlewares",
    "middleware": "tigrbl_concrete._decorators.middlewares",
    "middlewares": "tigrbl_concrete._decorators.middlewares",
    # rest
    "get": "tigrbl_concrete._decorators.rest",
    "post": "tigrbl_concrete._decorators.rest",
    "put": "tigrbl_concrete._decorators.rest",
    "patch": "tigrbl_concrete._decorators.rest",
    "delete": "tigrbl_concrete._decorators.rest",
    "route_ctx": "tigrbl_concrete._decorators.router",
    "route": "tigrbl_concrete._decorators.router",
    # authn
    "allow_anon": "tigrbl_concrete._decorators.allow_anon",
    # response
    "response_ctx": "tigrbl_concrete._decorators.response",
    "get_attached_response_alias": "tigrbl_concrete._decorators.response",
    "get_attached_response_spec": "tigrbl_concrete._decorators.response",
}


__all__ = list(_EXPORTS)


def __getattr__(name: str) -> Any:
    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(name)
    module = import_module(module_name)
    return getattr(module, name)
