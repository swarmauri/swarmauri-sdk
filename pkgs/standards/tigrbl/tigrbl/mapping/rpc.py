"""Compatibility alias to canon RPC mapping module."""

from importlib import import_module
import sys

sys.modules[__name__] = import_module("tigrbl_canon.mapping.rpc")
