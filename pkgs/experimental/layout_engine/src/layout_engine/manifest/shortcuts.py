from __future__ import annotations
import json
from typing import Mapping, Any
from .default import build_manifest as _build, to_dict as _to_dict, from_dict as _from_dict, diff as _diff, apply_patch as _apply, schema as _schema
from .spec import Manifest

def build(view_model: Mapping[str, Any]) -> Manifest:
    return _build(view_model)

def to_json(manifest: Manifest) -> str:
    return json.dumps(_to_dict(manifest), separators=(",", ":"), sort_keys=True)

def from_json(data: str) -> Manifest:
    return _from_dict(json.loads(data))

def patch(old: Manifest, new: Manifest) -> dict:
    return _diff(old, new)

def apply(manifest: Manifest, patch: Mapping[str, Any]) -> Manifest:
    return _apply(manifest, patch)

def schema() -> dict:
    return _schema()
