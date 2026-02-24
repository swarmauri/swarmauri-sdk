"""Manifest: canonical, framework-agnostic description of a rendered page.

Exports:
- `Manifest` dataclass
- Builder: `ManifestBuilder` and `build_manifest(view_model, version=...)`
- Utilities: `etag_of(obj)`, `to_dict(manifest)`, `from_dict(data)`
- Validation & schema: `validate(manifest)`, `schema()`
- Patching: `diff(old, new)`, `apply_patch(base, patch)`
"""

from .spec import Manifest, SiteManifest, ChannelManifest, WsRouteManifest
from .default import ManifestBuilder
from .utils import (
    build_manifest,
    etag_of,
    to_dict,
    from_dict,
    validate,
    schema,
    diff,
    apply_patch,
    manifest_to_json,
    manifest_from_json,
    compute_etag,
    validate_manifest,
    sort_tiles,
    to_plain_dict,
    from_plain_dict,
    diff_manifests,
    make_patch,
)

__all__ = [
    "Manifest",
    "SiteManifest",
    "ChannelManifest",
    "WsRouteManifest",
    "SiteManifest",
    "ManifestBuilder",
    "build_manifest",
    "etag_of",
    "to_dict",
    "from_dict",
    "validate",
    "schema",
    "diff",
    "apply_patch",
    "manifest_to_json",
    "manifest_from_json",
    "compute_etag",
    "validate_manifest",
    "sort_tiles",
    "to_plain_dict",
    "from_plain_dict",
    "diff_manifests",
    "make_patch",
]
