from __future__ import annotations

from typing import Any, Iterable, Mapping, Type

from pydantic import BaseModel
from layout_engine import AtomSpec

from ..default import AtomPresetCatalog
from ..spec import AtomPreset


class AtomProps(BaseModel):
    """Loose schema for SwarmaKit atom props (override per framework atom)."""

    model_config = {"extra": "allow"}


class SwarmaAtomCatalog(AtomPresetCatalog):
    """Catalog adapter that adds Swarma-specific helpers on top of presets."""

    def __init__(
        self,
        presets: Mapping[str, AtomPreset | AtomSpec] | Iterable[AtomPreset | AtomSpec],
        *,
        props_schema: Type[AtomProps] = AtomProps,
    ):
        self._props_schema = props_schema
        normalized = self._normalize_presets(presets)
        super().__init__(normalized)

    @property
    def props_schema(self) -> Type[AtomProps]:
        return self._props_schema

    def get_spec(self, role: str) -> AtomSpec:
        return self.get(role).to_spec()

    def merge_props(
        self, role: str, overrides: Mapping[str, Any] | None = None
    ) -> dict[str, Any]:
        preset = self.get(role)
        merged = {**dict(preset.defaults), **(overrides or {})}
        return self._props_schema(**merged).model_dump()

    def with_overrides(self, role: str, **patch: Any) -> "SwarmaAtomCatalog":
        """Return a new catalog with the given role patched (e.g., defaults/version)."""

        if role not in self._presets:
            raise KeyError(f"Unknown Swarma atom role: {role}")

        updated = self._presets[role].model_copy(update=patch)
        presets = dict(self._presets)
        presets[role] = updated
        return self.__class__(presets, props_schema=self._props_schema)

    def with_extra_presets(
        self,
        extra_presets: Mapping[str, AtomPreset | AtomSpec]
        | Iterable[AtomPreset | AtomSpec],
    ) -> "SwarmaAtomCatalog":
        presets = dict(self._presets)
        updates = self._normalize_presets(extra_presets)
        presets.update(updates)
        return self.__class__(presets, props_schema=self._props_schema)

    @staticmethod
    def _ensure_preset(value: AtomPreset | AtomSpec) -> AtomPreset:
        if isinstance(value, AtomPreset):
            return value
        if isinstance(value, AtomSpec):
            return AtomPreset(
                role=value.role,
                module=value.module,
                export=value.export,
                version=value.version,
                defaults=dict(value.defaults),
                family=getattr(value, "family", None),
                framework=getattr(value, "framework", None),
                package=getattr(value, "package", None),
                tokens=dict(getattr(value, "tokens", {}) or {}),
                registry=dict(getattr(value, "registry", {}) or {}),
            )
        raise TypeError(f"Unsupported preset payload type: {type(value)!r}")

    @classmethod
    def _normalize_presets(
        cls,
        data: Mapping[str, AtomPreset | AtomSpec] | Iterable[AtomPreset | AtomSpec],
    ) -> dict[str, AtomPreset]:
        if isinstance(data, Mapping):
            normalized: dict[str, AtomPreset] = {}
            for candidate in data.values():
                preset = cls._ensure_preset(candidate)
                normalized[preset.role] = preset
            return normalized
        normalized: dict[str, AtomPreset] = {}
        for candidate in data:
            preset = cls._ensure_preset(candidate)
            normalized[preset.role] = preset
        return normalized
