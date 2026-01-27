"""Micro-frontend (MFE) registry and import-map utilities.

This module is framework-agnostic. It describes **remotes** (composite apps)
and produces an **import map** the host (Svelte/Vue/React/HTML) can consume.
"""

from .spec import (
    Remote,
    Framework,
    validate_id,
    validate_framework,
    validate_entry,
    validate_exposed,
)
from .base import IRemoteRegistry, IImportMapBuilder
from .default import RemoteRegistry, ImportMapBuilder
from .shortcuts import (
    remote,
    remotes,
    build_import_map,
    import_map_script,
    modulepreload_links,
    import_map_json,
    compose_import_maps,
)
from .decorators import (
    remote as remote_deco,
    remote_ctx,
    require_integrity,
    stable_entry,
)
from .bindings import (
    to_dict,
    from_dict,
    registry_to_dict,
    registry_from_dict,
    to_import_map,
    to_import_map_json,
    script_tag,
    modulepreload_html,
)

__all__ = [
    "Remote",
    "Framework",
    "validate_id",
    "validate_framework",
    "validate_entry",
    "validate_exposed",
    "IRemoteRegistry",
    "IImportMapBuilder",
    "RemoteRegistry",
    "ImportMapBuilder",
    "remote",
    "remotes",
    "build_import_map",
    "import_map_script",
    "modulepreload_links",
    "import_map_json",
    "compose_import_maps",
    "remote_deco",
    "remote_ctx",
    "stable_entry",
    "require_integrity",
    "to_dict",
    "from_dict",
    "registry_to_dict",
    "registry_from_dict",
    "to_import_map",
    "to_import_map_json",
    "script_tag",
    "modulepreload_html",
]
