from __future__ import annotations

from typing import Any, Mapping

from ..atoms import AtomRegistry, AtomSpec

try:  # pragma: no cover - exercised via runtime import in tests
    from layout_engine_atoms import (  # type: ignore[import-not-found]
        DEFAULT_ATOMS as _DEFAULT_ATOMS,
        build_default_registry as _build_default_registry,
    )
except Exception:  # noqa: BLE001 - degrade gracefully if package missing
    _FALLBACK_PRESETS: Mapping[str, Mapping[str, Any]] = {
        "ui:text:body": {
            "module": "@swarmauri/atoms/Typography",
            "export": "BodyText",
            "defaults": {"variant": "body", "weight": "regular"},
        },
        "ui:button:primary": {
            "module": "@swarmauri/atoms/Button",
            "export": "PrimaryButton",
            "defaults": {"kind": "primary", "size": "md"},
        },
        "viz:metric:kpi": {
            "module": "@swarmauri/atoms/Metrics",
            "export": "KpiCard",
            "defaults": {"format": "compact", "sparkline": False},
        },
    }

    DEFAULT_ATOMS: dict[str, AtomSpec] = {
        role: AtomSpec(
            role=role,
            module=str(data["module"]),
            export=str(data.get("export", "default")),
            defaults=dict(data.get("defaults", {})),
        )
        for role, data in _FALLBACK_PRESETS.items()
    }

    def build_default_registry() -> AtomRegistry:
        registry = AtomRegistry()
        registry.register_many(DEFAULT_ATOMS.values())
        return registry

else:
    DEFAULT_ATOMS = dict(_DEFAULT_ATOMS)

    def build_default_registry() -> AtomRegistry:
        return _build_default_registry()


__all__ = ["DEFAULT_ATOMS", "build_default_registry"]
