"""Compatibility alias to canon op MRO collector module."""

from importlib import import_module
import sys

sys.modules[__name__] = import_module("tigrbl_canon.mapping.op_mro_collect")
