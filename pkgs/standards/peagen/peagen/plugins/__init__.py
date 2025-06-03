# peagen/plugin_registry.py
"""Plugin registry for the Peagen microkernel."""

from importlib.metadata import entry_points
from collections import defaultdict
from types import ModuleType
from typing import Dict

# ---------------------------------------------------------------------------
# Config – group key → (entry-point group string, expected base class)
# ---------------------------------------------------------------------------
GROUPS = {
    "consumers": ("peagen.plugins.consumers", object),
    "evaluator_pools": ("peagen.plugins.evaluator_pools", object),
    "evaluators": ("peagen.plugins.evaluators", object),
    "indexers": ("peagen.plugins.indexers", object),
    "mutators": ("peagen.plugins.mutators", object),
    "programs": ("peagen.plugins.programs", object),
    "publishers": ("peagen.plugins.publishers", object),
    "queues": ("peagen.plugins.queues", object),
    "result_backends": ("peagen.plugins.result_backends", object),
    "storage_adapters": ("peagen.plugins.storage_adapters", object),
    "selectors": ("peagen.plugins.selectors", object),
    "template_sets": ("peagen.template_sets", None),
}

registry: Dict[str, Dict[str, object]] = defaultdict(dict)


def discover_and_register_plugins(
    mode: str = "fan-out", switch_map: dict[str, str] | None = None
) -> None:
    """Discover entry-point plugins and register them.

    Parameters
    ----------
    mode:
        ``"fan-out"`` loads every discovered plugin. ``"fallback"`` prefers
        built-ins when names clash. ``"switch"`` only loads the plugin named in
        ``switch_map`` for each group, falling back to built-ins.
    switch_map:
        Optional mapping of ``group_key`` → ``plugin_name`` for ``"switch"`` mode.
    """

    switch_map = switch_map or {}

    for group_key, (ep_group, base_cls) in GROUPS.items():
        eps = list(entry_points(group=ep_group))
        builtins = [ep for ep in eps if ep.module.startswith("peagen.")]
        others = [ep for ep in eps if not ep.module.startswith("peagen.")]

        if mode == "switch":
            chosen = builtins[:]
            target = switch_map.get(group_key)
            if target:
                chosen.extend(ep for ep in others if ep.name == target)
            eps_to_process = chosen
        else:
            eps_to_process = builtins + others

        for ep in eps_to_process:
            obj = ep.load()

            if ep.name in registry[group_key]:
                existing = registry[group_key][ep.name]
                if existing is obj:
                    continue
                if mode == "fallback":
                    continue
                raise RuntimeError(
                    f"Duplicate plugin name '{ep.name}' detected in group '{group_key}'."
                )

            if group_key == "template_sets":
                if not (isinstance(obj, ModuleType) or isinstance(obj, type)):
                    raise TypeError(
                        f"Entry-point '{ep.name}' in group '{ep_group}' "
                        f"resolved to {type(obj).__name__}; expected a module or class."
                    )
            else:
                if not isinstance(obj, type):
                    raise TypeError(
                        f"Entry-point '{ep.name}' in group '{ep_group}' "
                        f"resolved to {type(obj).__name__}; expected a class."
                    )
                if not issubclass(obj, base_cls):
                    raise TypeError(
                        f"Entry-point '{ep.name}' in group '{ep_group}' must subclass {base_cls.__name__}."
                    )

            registry[group_key][ep.name] = obj
