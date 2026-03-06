"""Compatibility wrapper for runtime atoms namespace."""

from importlib import import_module
from pkgutil import extend_path

_atoms = import_module("tigrbl_atoms.atoms")
__path__ = extend_path(__path__, __name__)
__path__.extend(list(getattr(_atoms, "__path__", [])))

from tigrbl_atoms.atoms import *  # noqa: E402,F401,F403
