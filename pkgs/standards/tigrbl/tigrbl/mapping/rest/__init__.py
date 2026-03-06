"""Compatibility wrapper for mapping REST namespace."""

from importlib import import_module
from pkgutil import extend_path

_rest = import_module("tigrbl_canon.mapping.rest")
__path__ = extend_path(__path__, __name__)
__path__.extend(list(getattr(_rest, "__path__", [])))

from tigrbl_canon.mapping.rest import *  # noqa: E402,F401,F403
