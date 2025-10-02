"""Manifest: canonical, framework-agnostic description of a rendered page.

Exports:
- `Manifest` dataclass
- Builder: `build_manifest(view_model, version=...)`
- Utilities: `etag_of(obj)`, `to_dict(manifest)`, `from_dict(data)`
- Validation & schema: `validate(manifest)`, `schema()`
- Patching: `diff(old, new)`, `apply_patch(base, patch)`
"""
from .spec import Manifest
from .default import (
    build_manifest, etag_of, to_dict, from_dict, validate, schema,
    diff, apply_patch
)

__all__ = [
    "Manifest",
    "build_manifest", "etag_of", "to_dict", "from_dict",
    "validate", "schema", "diff", "apply_patch",
]
