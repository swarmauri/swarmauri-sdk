from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable

from layout_engine import ComponentRegistry, ComponentSpec

SWARMAKIT_VUE_PRESETS: Dict[str, Dict[str, Any]] = {
    "avatar": {
        "module": "@swarmakit/vue",
        "export": "Avatar",
        "defaults": {
            "imageSrc": "https://example.com/avatar.png",
            "initials": "AA",
            "ariaLabel": "Avatar",
        },
    },
    "notification": {
        "module": "@swarmakit/vue",
        "export": "Notification",
        "defaults": {
            "notificationType": "success",
            "message": "All systems operational.",
            "isDismissed": False,
        },
    },
    "progress": {
        "module": "@swarmakit/vue",
        "export": "ProgressBar",
        "defaults": {
            "progress": 42,
            "disabled": False,
        },
    },
    "table": {
        "module": "@swarmakit/vue",
        "export": "DataGrid",
        "defaults": {
            "headers": ["Column", "Value"],
            "data": [["Example", "42"]],
            "paginationEnabled": True,
            "searchEnabled": False,
            "resizable": True,
            "itemsPerPage": 5,
        },
    },
    "timeline": {
        "module": "@swarmakit/vue",
        "export": "TimelineList",
        "defaults": {
            "items": [
                {"id": 1, "label": "Draft", "completed": True},
                {"id": 2, "label": "Review", "completed": False},
            ],
            "activeIndex": 1,
        },
    },
}


def get_swarmakit_presets(
    overrides: Dict[str, Dict[str, Any]] | None = None,
) -> Dict[str, Dict[str, Any]]:
    """Return a deep copy of the Swarmakit presets merged with optional overrides."""

    merged: Dict[str, Dict[str, Any]] = deepcopy(SWARMAKIT_VUE_PRESETS)
    if not overrides:
        return merged

    for role, config in overrides.items():
        base = deepcopy(merged.get(role, {}))
        candidate = deepcopy(config)
        if base and "defaults" in base and "defaults" in candidate:
            defaults = {**base["defaults"], **candidate["defaults"]}
            candidate = {**base, **candidate, "defaults": defaults}
        merged[role] = candidate
    return merged


def create_swarmakit_registry(
    roles: Iterable[str],
    *,
    overrides: Dict[str, Dict[str, Any]] | None = None,
) -> ComponentRegistry:
    """Create a ``ComponentRegistry`` pre-populated with Swarmakit Vue presets."""

    presets = get_swarmakit_presets(overrides)
    registry = ComponentRegistry()
    for role in sorted(set(roles)):
        atom = presets.get(role)
        if not atom:
            raise KeyError(f"No Swarmakit preset registered for role {role!r}")
        spec = ComponentSpec(
            role=role,
            module=atom["module"],
            export=atom.get("export", "default"),
            defaults=atom.get("defaults", {}),
        )
        registry.register(spec)
    return registry


__all__ = [
    "SWARMAKIT_VUE_PRESETS",
    "create_swarmakit_registry",
    "get_swarmakit_presets",
]
