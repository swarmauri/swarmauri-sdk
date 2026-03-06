"""Compatibility alias to canon REST member module."""

from importlib import import_module
import sys

sys.modules[__name__] = import_module("tigrbl_canon.mapping.rest.member")
