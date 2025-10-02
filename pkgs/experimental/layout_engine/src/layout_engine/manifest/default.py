from __future__ import annotations
import json, hashlib
from typing import Any, Mapping

from .spec import Manifest

# --------- Core utilities ---------

def etag_of(obj: Mapping[str, Any]) -> str:
    """Stable content hash (sha256 over canonical JSON)."""
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()

def _normalize_tile(tile: Mapping[str, Any]) -> dict:
    """Normalize a tile payload to a canonical structure & field order.

    Required keys:
      - id (str), role (str), frame (mapping x,y,w,h), props (mapping)
    Optional:
      - component (mapping: module/export/version/defaults)
    Unknown keys are preserved for forward-compat but serialized at the end.
    """
    t = dict(tile)
    tid = str(t.get("id"))
    role = str(t.get("role"))
    frame = dict(t.get("frame") or {})
    props = dict(t.get("props") or {})
    component = t.get("component")
    base = {
        "id": tid,
        "role": role,
        "frame": {"x": int(frame.get("x", 0)), "y": int(frame.get("y", 0)),
                  "w": int(frame.get("w", 0)), "h": int(frame.get("h", 0))},
        "props": props,
    }
    if component is not None:
        c = dict(component)
        base["component"] = {
            "module": str(c.get("module", "")),
            "export": str(c.get("export", "default")),
            "version": str(c.get("version", "1.0.0")),
            "defaults": dict(c.get("defaults", {})),
        }
    # Append any extra keys deterministically
    for k in sorted(t.keys()):
        if k not in base:
            base[k] = t[k]
    return base

def _normalize_view_model(vm: Mapping[str, Any]) -> dict:
    vp = dict(vm.get("viewport") or {})
    grid = dict(vm.get("grid") or {})
    tiles = list(vm.get("tiles") or [])
    # normalize tiles and ensure id uniqueness
    norm_tiles = [_normalize_tile(t) for t in tiles]
    seen = set()
    uniq = []
    for t in norm_tiles:
        if t["id"] in seen:
            # last occurrence wins
            uniq = [u for u in uniq if u["id"] != t["id"]]
        seen.add(t["id"])
        uniq.append(t)
    # stable ordering by id for deterministic etag unless caller already sorted
    uniq.sort(key=lambda x: x["id"])
    return {
        "kind": "layout_manifest",
        "version": str(vm.get("version", "2025.10")),
        "viewport": {"width": int(vp.get("width", 1280)), "height": int(vp.get("height", 800))},
        "grid": grid,
        "tiles": uniq,
    }

# --------- Builder / (De)serialization ---------

def build_manifest(view_model: Mapping[str, Any], *, version: str | None = None) -> Manifest:
    payload = _normalize_view_model(view_model)
    if version is not None:
        payload["version"] = version
    return Manifest(**payload, etag=etag_of(payload))

def to_dict(manifest: Manifest) -> dict:
    return {
        "kind": manifest.kind,
        "version": manifest.version,
        "viewport": dict(manifest.viewport),
        "grid": dict(manifest.grid),
        "tiles": [dict(t) for t in manifest.tiles],
        "etag": manifest.etag,
    }

def from_dict(data: Mapping[str, Any]) -> Manifest:
    # Normalize again to ensure field ordering and computed types are clean
    payload = _normalize_view_model(data)
    etag = str(data.get("etag") or etag_of(payload))
    return Manifest(**payload, etag=etag)

# --------- Validation & schema ---------

def validate(manifest: Manifest) -> None:
    if manifest.kind != "layout_manifest":
        raise ValueError("manifest.kind must be 'layout_manifest'")
    vp = manifest.viewport
    for k in ("width","height"):
        if k not in vp or not isinstance(vp[k], int) or vp[k] < 0:
            raise ValueError(f"viewport.{k} must be a non-negative int")
    # basic tile checks
    seen = set()
    for t in manifest.tiles:
        if "id" not in t or "frame" not in t:
            raise ValueError("each tile must have 'id' and 'frame'")
        if t["id"] in seen:
            raise ValueError(f"duplicate tile id: {t['id']}")
        seen.add(t["id"])
        f = t["frame"]
        for k in ("x","y","w","h"):
            if k not in f or not isinstance(f[k], int):
                raise ValueError(f"tile {t['id']} frame.{k} must be int")

def schema() -> dict:
    """Minimal JSON schema for interoperability and validation in adapters."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Layout Manifest",
        "type": "object",
        "required": ["kind","version","viewport","grid","tiles","etag"],
        "properties": {
            "kind": {"const": "layout_manifest"},
            "version": {"type": "string"},
            "viewport": {
                "type": "object",
                "required": ["width","height"],
                "properties": {
                    "width": {"type": "integer", "minimum": 0},
                    "height": {"type": "integer", "minimum": 0}
                }
            },
            "grid": {"type": "object"},
            "tiles": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["id","role","frame","props"],
                    "properties": {
                        "id": {"type": "string"},
                        "role": {"type": "string"},
                        "frame": {
                            "type": "object",
                            "required": ["x","y","w","h"],
                            "properties": {
                                "x": {"type": "integer"}, "y": {"type": "integer"},
                                "w": {"type": "integer"}, "h": {"type": "integer"},
                            }
                        },
                        "props": {"type": "object"},
                        "component": {
                            "type": "object",
                            "properties": {
                                "module": {"type": "string"},
                                "export": {"type": "string"},
                                "version": {"type": "string"},
                                "defaults": {"type": "object"},
                            }
                        }
                    }
                }
            },
            "etag": {"type": "string"}
        },
        "additionalProperties": False
    }

# --------- Diff / Patch ---------

def _frame_map(manifest: Manifest) -> dict[str, dict]:
    return {t["id"]: dict(t["frame"]) for t in manifest.tiles}

def diff(old: Manifest, new: Manifest, *, epsilon: int = 0) -> dict:
    """Compute a simple manifest patch focused on geometry and tile set.
    Returns:
      {
        "base_etag": str,
        "etag": str,
        "added": [ids], "removed": [ids], "changed": [ids], "unchanged": [ids],
        "frames": { id: {x,y,w,h} }   # for added+changed
      }
    """
    a = _frame_map(old); b = _frame_map(new)
    old_keys = set(a); new_keys = set(b)
    added = sorted(new_keys - old_keys)
    removed = sorted(old_keys - new_keys)
    changed = []
    unchanged = []
    frames = {}

    for tid in sorted(old_keys & new_keys):
        fa = a[tid]; fb = b[tid]
        if abs(fa["x"]-fb["x"])<=epsilon and abs(fa["y"]-fb["y"])<=epsilon and abs(fa["w"]-fb["w"])<=epsilon and abs(fa["h"]-fb["h"])<=epsilon:
            unchanged.append(tid)
        else:
            changed.append(tid); frames[tid] = fb
    for tid in added:
        frames[tid] = b[tid]

    return {
        "base_etag": old.etag,
        "etag": new.etag,
        "added": added, "removed": removed, "changed": changed, "unchanged": unchanged,
        "frames": frames
    }

def apply_patch(base: Manifest, patch: Mapping[str, Any]) -> Manifest:
    """Apply a geometry-only patch produced by `diff`.

    If `patch['base_etag']` doesn't match `base.etag`, the caller is responsible
    for reconciling; we still apply to allow last-wins behavior in clients.
    """
    base_d = to_dict(base)
    tiles = {t["id"]: dict(t) for t in base_d["tiles"]}
    # Remove tiles
    for tid in patch.get("removed", []):
        tiles.pop(tid, None)
    # Add/update frames
    for tid, fr in (patch.get("frames") or {}).items():
        if tid not in tiles:
            tiles[tid] = {"id": tid, "role": "", "props": {}, "frame": {"x":0,"y":0,"w":0,"h":0}}
        tiles[tid]["frame"] = {k:int(fr[k]) for k in ("x","y","w","h")}

    base_d["tiles"] = sorted(tiles.values(), key=lambda t: t["id"])
    base_d["etag"] = patch.get("etag", base.etag)
    return from_dict(base_d)
