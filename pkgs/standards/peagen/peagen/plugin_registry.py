# peagen/plugin_registry.py
"""
peagen.plugin_registry

Maintain the plugin registry loaded from distribution entry points.

``registry`` maps plugin groups to dictionaries of ``{name: object}``.
For example::

    registry = {
        "template_sets":    {"init-ci": <module>, ...},
        "storage_adapters": {"file": <class FileStorageAdapter>, ...},
        ...
    }

``_load()`` discovers entry points for each group defined in ``GROUPS``,
validates them and populates this mapping at import time. Supported plugin
groups are: ``template_sets``, ``storage_adapters``, ``publishers``,
``indexers``, ``result_backends`` and ``evaluators``.
"""

from importlib.metadata import entry_points
from collections import defaultdict
from typing import Dict
from types import ModuleType

# ---------------------------------------------------------------------------
# Config – group key → (entry-point group string, expected base class)
# We’ll special-case "template_sets" so it can resolve to ModuleType or class,
# and treat every other group as before (must resolve to a class).
# ---------------------------------------------------------------------------
GROUPS = {
    "template_sets": ("peagen.template_sets", None),  # None = allow modules or classes
    "storage_adapters": ("peagen.storage_adapters", object),
    "publishers": ("peagen.publishers", object),
    "indexers": ("peagen.indexers", object),
    "result_backends": ("peagen.result_backends", object),
    "evaluators": ("peagen.evaluators", object),
}

registry: Dict[str, Dict[str, object]] = defaultdict(dict)


def _load() -> None:
    """
    Discover every plugin exactly once at import time.
    Populates the `registry` mapping:
      registry = {
        "template_sets":    {"init-ci": <module '...'>, ...},
        "storage_adapters": {"file": <class FileStorageAdapter>, ...},
        ...
      }
    """
    for group_key, (ep_group, base_cls) in GROUPS.items():
        for ep in entry_points(group=ep_group):
            obj = ep.load()

            # ─── template_sets: allow modules or classes ──────────────────────
            if group_key == "template_sets":
                if not (isinstance(obj, ModuleType) or isinstance(obj, type)):
                    raise TypeError(
                        f"Entry-point '{ep.name}' in group '{ep_group}' "
                        f"resolved to {type(obj).__name__}; expected a module or class."
                    )

            # ─── other groups: must be a class and subclass of base_cls ────────
            else:
                if not isinstance(obj, type):
                    raise TypeError(
                        f"Entry-point '{ep.name}' in group '{ep_group}' "
                        f"resolved to {type(obj).__name__}; expected a class."
                    )
                if not issubclass(obj, base_cls):
                    raise TypeError(
                        f"Entry-point '{ep.name}' in group '{ep_group}' "
                        f"must subclass {base_cls.__name__}."
                    )

            # ─── no duplicate names on the same group ─────────────────────────
            if ep.name in registry[group_key]:
                raise RuntimeError(
                    f"Duplicate plugin name '{ep.name}' detected in group "
                    f"'{group_key}'."
                )

            registry[group_key][ep.name] = obj


# run discovery immediately on import
_load()
