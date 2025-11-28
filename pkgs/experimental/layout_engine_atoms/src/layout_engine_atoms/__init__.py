"""Swarmauri atom presets for layout-engine."""

# Manifest helpers
from .manifest import (
    Tile as ManifestTile,
    build_manifest_from_tiles,
    build_manifest_from_table,
    create_registry as create_manifest_registry,
    quick_manifest,
    quick_manifest_from_table,
    tile as manifest_tile,
)

from .spec import AtomPreset
from .default import IAtomCatalog, AtomPresetCatalog
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

# Runtime exports
from .runtime.vue import (
    mount_layout_app,
    UiEvent,
    UiEventResult,
    LayoutOptions,
    RouterOptions,
    ScriptSpec,
    UIHooks,
    RealtimeOptions,
    RealtimeChannel,
    RealtimeBinding,
)

__all__ = [
    "AtomPreset",
    "IAtomCatalog",
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
    "ManifestTile",
    "manifest_tile",
    "create_manifest_registry",
    "quick_manifest",
    "build_manifest_from_tiles",
    "quick_manifest_from_table",
    "build_manifest_from_table",
    # Runtime
    "mount_layout_app",
    "UiEvent",
    "UiEventResult",
    "LayoutOptions",
    "RouterOptions",
    "ScriptSpec",
    "UIHooks",
    "RealtimeOptions",
    "RealtimeChannel",
    "RealtimeBinding",
]
