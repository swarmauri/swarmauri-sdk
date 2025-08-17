# tests/perf/utils.py
from __future__ import annotations

import sys
import types
from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

from swarmauri.interface_registry import InterfaceRegistry

SW_PREFIX = "swarmauri."

@dataclass
class FakeEntryPoint:
    """
    Minimal EntryPoint-like object sufficient for plugin_manager.
    """
    name: str       # type name, e.g. "PerfPlugin_AgentBase_0001"
    value: str      # "module.path:ClassName" or "module.path" (module plugin)
    group: str      # e.g., "swarmauri.agents"
    dist: object | None = None
    _loader: Callable[[], object] | None = None

    def load(self):
        if self._loader is None:
            raise RuntimeError("No loader provided for FakeEntryPoint")
        return self._loader()


def _create_dynamic_module(module_name: str) -> types.ModuleType:
    mod = types.ModuleType(module_name)
    # Make subsequent imports find this module.
    sys.modules[module_name] = mod
    return mod


def _class_loader(module_name: str, class_name: str, base_cls: type):
    """
    Returns a callable that, when invoked, creates a module and a class
    deriving from base_cls, and returns the class (class-based plugin).
    """
    def _load():
        mod = _create_dynamic_module(module_name)
        cls = type(class_name, (base_cls,), {"__module__": module_name})
        setattr(mod, class_name, cls)
        mod.__all__ = [class_name]
        return cls
    return _load


def _module_loader(module_name: str, class_name: str, base_cls: type):
    """
    Returns a callable that creates a module with __all__ exposing a single
    class deriving from base_cls, and returns the module (module-based plugin).
    """
    def _load():
        mod = _create_dynamic_module(module_name)
        cls = type(class_name, (base_cls,), {"__module__": module_name})
        setattr(mod, class_name, cls)
        mod.__all__ = [class_name]
        return mod
    return _load


def select_groups(count: int) -> List[str]:
    """
    Pick `count` registered swarmauri namespaces (e.g., "swarmauri.agents", ...).
    """
    all_namespaces = [ns for ns in InterfaceRegistry.list_registered_namespaces() if ns.startswith(SW_PREFIX)]
    if count > len(all_namespaces):
        raise ValueError(f"Requested {count} groups but only {len(all_namespaces)} are registered.")
    return all_namespaces[:count]


def build_grouped_fake_entry_points(
    groups: List[str],
    total_plugins: int,
    *,
    mode: str = "class",  # "class" or "module"
    type_prefix: str = "PerfPlugin",
) -> Dict[str, List[FakeEntryPoint]]:
    """
    Build a grouped dict: { short_namespace: [FakeEntryPoint, ...], ... }
    matching plugin_manager.get_entry_points() output shape.
    """
    if mode not in {"class", "module"}:
        raise ValueError("mode must be 'class' or 'module'")

    # Even distribution with remainder spread over the first groups
    per_group = total_plugins // max(1, len(groups))
    remainder = total_plugins - per_group * len(groups)

    result: Dict[str, List[FakeEntryPoint]] = {}
    counter = 0

    for idx, group in enumerate(groups):
        # Example: group="swarmauri.agents" => short="agents"
        short = group[len(SW_PREFIX):]
        result[short] = []

        # Base interface for this resource group
        base_cls = InterfaceRegistry.get_interface_for_resource(group)

        # how many plugins in this group
        n_here = per_group + (1 if idx < remainder else 0)

        for i in range(n_here):
            counter += 1
            class_name = f"{type_prefix}_{base_cls.__name__}_{counter:04d}"

            module_name = f"swarmauri_test_plugins.{short}.{class_name.lower()}"
            if mode == "class":
                value = f"{module_name}:{class_name}"
                loader = _class_loader(module_name, class_name, base_cls)
            else:
                value = f"{module_name}"
                loader = _module_loader(module_name, class_name, base_cls)

            ep = FakeEntryPoint(
                name=class_name,
                value=value,
                group=group,
                dist=None,           # No dist => metadata lookup is skipped
                _loader=loader,
            )
            result[short].append(ep)

    return result
