"""Compatibility wrapper for :mod:`peagen.transport.jsonrpc_schemas`."""

from importlib import import_module
import sys

# Re-export all names from the canonical package
from peagen.transport.jsonrpc_schemas import *  # noqa: F401,F403

# Provide submodule aliases so imports like
# ``peagen.transport.json_rpcschemas.task`` work as expected.
_submods = [
    "guard",
    "keys",
    "pool",
    "secrets",
    "task",
    "work",
    "worker",
]
for _m in _submods:
    sys.modules[__name__ + "." + _m] = import_module(
        f"peagen.transport.jsonrpc_schemas.{_m}"
    )

del import_module, sys, _submods
