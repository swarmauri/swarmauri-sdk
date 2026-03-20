"""Compatibility module exposing ``tigrbl_orm.orm`` as ``tigrbl.orm``."""

from __future__ import annotations

from importlib import import_module
import sys

_target = import_module("tigrbl_orm.orm")

for _name, _value in vars(_target).items():
    if _name.startswith("__") and _name not in {"__doc__", "__all__", "__path__"}:
        continue
    globals()[_name] = _value

__doc__ = getattr(_target, "__doc__", __doc__)
__all__ = getattr(_target, "__all__", [])
__path__ = list(getattr(_target, "__path__", []))

_target_prefix = "tigrbl_orm.orm"
_alias_prefix = "tigrbl.orm"
for _module_name, _module in tuple(sys.modules.items()):
    if _module_name.startswith(f"{_target_prefix}."):
        _suffix = _module_name[len(_target_prefix) :]
        sys.modules.setdefault(f"{_alias_prefix}{_suffix}", _module)
