"""Swarmauri atom presets for layout-engine."""

from .spec import AtomPreset
from .default import AtomPresetCatalog
from .shortcuts import (
    build_registry as build_registry_from_presets,
    load_catalog as load_catalog_from_data,
    presets_from_specs,
)
from .catalog import (
    DEFAULT_ATOMS,
    DEFAULT_PRESETS,
    PRESET_VERSION,
    SUPPORTED_CATALOGS,
    build_catalog,
    build_default_registry,
    build_registry,
    get_default_atoms,
    get_default_presets,
    get_preset_version,
    load_catalog,
)

__all__ = [
    "AtomPreset",
    "AtomPresetCatalog",
    "DEFAULT_ATOMS",
    "DEFAULT_PRESETS",
    "PRESET_VERSION",
    "SUPPORTED_CATALOGS",
    "build_catalog",
    "build_default_registry",
    "build_registry",
    "get_default_atoms",
    "get_default_presets",
    "get_preset_version",
    "load_catalog",
    "build_registry_from_presets",
    "load_catalog_from_data",
    "presets_from_specs",
]
