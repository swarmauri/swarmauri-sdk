"""Compatibility wrapper for runtime route atoms namespace."""

from importlib import import_module
from pkgutil import extend_path

_route = import_module("tigrbl_atoms.atoms.route")
__path__ = extend_path(__path__, __name__)
__path__.extend(list(getattr(_route, "__path__", [])))

from tigrbl_atoms.atoms.route import *  # noqa: E402,F401,F403
