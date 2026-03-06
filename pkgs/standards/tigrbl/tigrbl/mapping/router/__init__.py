"""Compatibility wrapper for mapping router namespace."""

from importlib import import_module
from pkgutil import extend_path

_router = import_module("tigrbl_canon.mapping.router")
__path__ = extend_path(__path__, __name__)
__path__.extend(list(getattr(_router, "__path__", [])))

from tigrbl_canon.mapping.router import *  # noqa: E402,F401,F403
