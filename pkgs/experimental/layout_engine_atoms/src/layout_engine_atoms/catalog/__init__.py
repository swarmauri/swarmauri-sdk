from __future__ import annotations

import importlib
from types import ModuleType
from typing import Iterable, Mapping

from layout_engine import AtomRegistry, AtomSpec

from ..default import AtomPresetCatalog
from ..spec import AtomPreset
from ..shortcuts import (
    build_registry as build_registry_from_data,
    load_catalog as load_catalog_from_data,
)

SUPPORTED_CATALOGS = ("vue", "svelte")

_CATALOG_MODULES = {
    "vue": "swarma_vue",
    "svelte": "swarma_svelte",
}


def _import_catalog(name: str) -> ModuleType:
    if name not in _CATALOG_MODULES:
        raise KeyError(
            f"Unknown atom catalog '{name}' (supported: {SUPPORTED_CATALOGS})"
        )
    module_name = _CATALOG_MODULES[name]
    return importlib.import_module(f"{__name__}.{module_name}")


def get_default_presets(name: str = "vue") -> Mapping[str, AtomPreset]:
    module = _import_catalog(name)
    return module.DEFAULT_PRESETS


def get_default_atoms(name: str = "vue") -> Mapping[str, AtomSpec]:
    module = _import_catalog(name)
    return module.DEFAULT_ATOMS


def get_preset_version(name: str = "vue") -> str:
    module = _import_catalog(name)
    return module.PRESET_VERSION


def load_catalog(name: str = "vue") -> AtomPresetCatalog:
    presets = get_default_presets(name)
    return load_catalog_from_data(presets)


def build_registry(
    name: str = "vue",
    *,
    extra_presets: Iterable[AtomPreset] | Mapping[str, AtomPreset] | None = None,
    overrides: Mapping[str, Mapping[str, object]] | None = None,
) -> AtomRegistry:
    presets = dict(get_default_presets(name))
    if extra_presets:
        if isinstance(extra_presets, Mapping):
            presets.update(extra_presets)
        else:
            presets.update({preset.role: preset for preset in extra_presets})
    if overrides:
        for role, patch in overrides.items():
            if role not in presets:
                continue
            presets[role] = presets[role].model_copy(update=patch)
    return build_registry_from_data(presets)


def build_catalog(name: str = "vue") -> AtomPresetCatalog:
    presets = get_default_presets(name)
    return AtomPresetCatalog(presets)


_vue_module = _import_catalog("vue")

DEFAULT_PRESETS = _vue_module.DEFAULT_PRESETS
DEFAULT_ATOMS = _vue_module.DEFAULT_ATOMS
PRESET_VERSION = _vue_module.PRESET_VERSION
build_default_registry = _vue_module.build_default_registry

__all__ = [
    "SUPPORTED_CATALOGS",
    "DEFAULT_PRESETS",
    "DEFAULT_ATOMS",
    "PRESET_VERSION",
    "build_default_registry",
    "build_catalog",
    "build_registry",
    "get_default_presets",
    "get_default_atoms",
    "get_preset_version",
    "load_catalog",
]
