"""Canonical decorators package for Tigrbl."""

from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORTS = {
    # op
    "AliasDecl": "tigrbl.decorators.op",
    "alias": "tigrbl.decorators.op",
    "alias_ctx": "tigrbl.decorators.op",
    "op_alias": "tigrbl.decorators.op",
    "op_ctx": "tigrbl.decorators.op",
    # hook
    "HOOK_DECLS_ATTR": "tigrbl.decorators.hook",
    "hook_ctx": "tigrbl.decorators.hook",
    # engine/schema/session
    "engine_ctx": "tigrbl.decorators.engine",
    "schema_ctx": "tigrbl.decorators.schema",
    "session_ctx": "tigrbl.decorators.session",
    "read_only_session": "tigrbl.decorators.session",
    # middleware
    "MiddlewareConfig": "tigrbl.decorators.middlewares",
    "middleware": "tigrbl.decorators.middlewares",
    "middlewares": "tigrbl.decorators.middlewares",
    # rest
    "get": "tigrbl.decorators.rest",
    "post": "tigrbl.decorators.rest",
    "put": "tigrbl.decorators.rest",
    "patch": "tigrbl.decorators.rest",
    "delete": "tigrbl.decorators.rest",
    "route_ctx": "tigrbl.decorators.router",
    "route": "tigrbl.decorators.router",
    # authn
    "allow_anon": "tigrbl.decorators.allow_anon",
    # response
    "response_ctx": "tigrbl.decorators.response",
    "get_attached_response_alias": "tigrbl.decorators.response",
    "get_attached_response_spec": "tigrbl.decorators.response",
}


__all__ = list(_EXPORTS)


def __getattr__(name: str) -> Any:
    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(name)
    module = import_module(module_name)
    return getattr(module, name)
