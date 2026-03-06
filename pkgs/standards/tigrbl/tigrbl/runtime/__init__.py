"""Compatibility namespace for runtime split package."""

from __future__ import annotations

from importlib import import_module
from pkgutil import iter_modules
import sys

_runtime = import_module("tigrbl_runtime.runtime")

# Mirror runtime submodules so legacy `tigrbl.runtime.<mod>` imports resolve to
# the same module objects as `tigrbl_runtime.runtime.<mod>`.
for _mod in iter_modules(getattr(_runtime, "__path__", ())):
    if _mod.name == "atoms":
        # Keep compatibility atoms namespace from this package.
        continue
    _target = import_module(f"tigrbl_runtime.runtime.{_mod.name}")
    sys.modules[f"{__name__}.{_mod.name}"] = _target

from tigrbl_runtime.runtime import *  # noqa: E402,F401,F403
