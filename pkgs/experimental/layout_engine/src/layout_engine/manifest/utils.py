from __future__ import annotations

import json
import hashlib
from typing import Any, Mapping, MutableMapping

from .spec import ChannelManifest, Manifest, SiteManifest, WsRouteManifest
from ..events.validators import ALLOW
from ..compile.utils import frame_diff
from ..core.frame import Frame


def etag_of(obj: Mapping[str, Any]) -> str:
    """Stable content hash (sha256 over canonical JSON)."""
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def _normalize_tile(tile: Mapping[str, Any]) -> dict:
    t = dict(tile)
    tid = str(t.get("id"))
    role = str(t.get("role"))
    frame = dict(t.get("frame") or {})
    props = dict(t.get("props") or {})
    atom = t.get("atom")
    base = {
        "id": tid,
        "role": role,
        "frame": {
            "x": int(frame.get("x", 0)),
            "y": int(frame.get("y", 0)),
            "w": int(frame.get("w", 0)),
            "h": int(frame.get("h", 0)),
        },
        "props": props,
    }
    if atom is not None:
        a = dict(atom)
        atom_payload = {
            "module": str(a.get("module", "")),
            "export": str(a.get("export", "default")),
            "version": str(a.get("version", "1.0.0")),
            "defaults": dict(a.get("defaults", {})),
        }
        optional_fields = (
            "role",
            "family",
            "framework",
            "package",
            "tokens",
            "registry",
        )
        for field in optional_fields:
            if field not in a or a[field] is None:
                continue
            if field in {"tokens", "registry"}:
                atom_payload[field] = dict(a.get(field, {}))
            else:
                atom_payload[field] = a[field]
        base["atom"] = atom_payload
    for k in sorted(t.keys()):
        if k not in base:
            base[k] = t[k]
    return base


def _normalize_site(
    site: Mapping[str, Any] | SiteManifest | None,
) -> SiteManifest | None:
    if site is None:
        return None
    if isinstance(site, SiteManifest):
        return site
    pages = site.get("pages") or []
    active = site.get("active_page") if "active_page" in site else site.get("active")
    navigation = dict(site.get("navigation") or {})
    return SiteManifest(pages=list(pages), active_page=active, navigation=navigation)


def _normalize_channels(
    channels: Mapping[str, Any] | ChannelManifest | list[Mapping[str, Any]] | None,
) -> list[dict[str, Any]]:
    if not channels:
        return []
    payload: list[dict[str, Any]] = []
    items = channels
    if isinstance(channels, Mapping) and not isinstance(channels, ChannelManifest):
        items = channels.values()
    if isinstance(items, ChannelManifest):
        items = [items]
    for entry in items:  # type: ignore[assignment]
        if isinstance(entry, ChannelManifest):
            payload.append(entry.model_dump())
        else:
            payload.append(ChannelManifest.model_validate(entry).model_dump())
    return payload


def _normalize_ws_routes(
    routes: Mapping[str, Any] | WsRouteManifest | list[Mapping[str, Any]] | None,
) -> list[dict[str, Any]]:
    if not routes:
        return []
    payload: list[dict[str, Any]] = []
    items = routes
    if isinstance(routes, Mapping) and not isinstance(routes, WsRouteManifest):
        items = routes.values()
    if isinstance(items, WsRouteManifest):
        items = [items]
    for entry in items:  # type: ignore[assignment]
        if isinstance(entry, WsRouteManifest):
            payload.append(entry.model_dump())
        else:
            payload.append(WsRouteManifest.model_validate(entry).model_dump())
    return payload


def _normalize_view_model(data: Mapping[str, Any]) -> dict:
    kind = str(data.get("kind") or "layout_manifest")
    version = str(data.get("version") or "2025.10")
    viewport = dict(data.get("viewport") or {})
    grid = data.get("grid") or {}
    tiles = [_normalize_tile(t) for t in data.get("tiles", [])]
    site = _normalize_site(data.get("site"))
    channels = _normalize_channels(data.get("channels"))
    ws_routes = _normalize_ws_routes(data.get("ws_routes"))
    return {
        "kind": kind,
        "version": version,
        "viewport": {
            "width": int(viewport.get("width", 0)),
            "height": int(viewport.get("height", 0)),
        },
        "grid": dict(grid),
        "tiles": tiles,
        "site": site.model_dump() if site else None,
        "channels": channels,
        "ws_routes": ws_routes,
    }


def build_manifest(
    view_model: Mapping[str, Any], *, version: str | None = None
) -> Manifest:
    payload = _normalize_view_model(view_model)
    if version is not None:
        payload["version"] = version
    etag_payload: MutableMapping[str, Any] = dict(payload)
    manifest = Manifest(**payload, etag=etag_of(etag_payload))
    if manifest.channels:
        try:
            from ..events.validators import register_channels as _register_channels
        except ImportError:
            pass
        else:
            _register_channels([channel.model_dump() for channel in manifest.channels])
    return manifest


def to_dict(manifest: Manifest) -> dict:
    data = {
        "kind": manifest.kind,
        "version": manifest.version,
        "viewport": dict(manifest.viewport),
        "grid": dict(manifest.grid),
        "tiles": [dict(t) for t in manifest.tiles],
        "etag": manifest.etag,
    }
    if manifest.site is not None:
        data["site"] = manifest.site.model_dump()
    if manifest.channels:
        data["channels"] = [channel.model_dump() for channel in manifest.channels]
    if manifest.ws_routes:
        data["ws_routes"] = [route.model_dump() for route in manifest.ws_routes]
    return data


def from_dict(data: Mapping[str, Any]) -> Manifest:
    payload = _normalize_view_model(data)
    etag = str(data.get("etag") or etag_of(payload))
    return Manifest(**payload, etag=etag)


def manifest_to_json(manifest: Manifest, *, indent: int | None = None) -> str:
    return json.dumps(to_dict(manifest), indent=indent, sort_keys=True)


def manifest_from_json(data: str | Mapping[str, Any]) -> Manifest:
    if isinstance(data, str):
        return from_dict(json.loads(data))
    return from_dict(data)


def validate(manifest: Manifest) -> None:
    if manifest.kind != "layout_manifest":
        raise ValueError("manifest.kind must be 'layout_manifest'")
    vp = manifest.viewport
    for k in ("width", "height"):
        if k not in vp or not isinstance(vp[k], int) or vp[k] < 0:
            raise ValueError(f"viewport.{k} must be a non-negative int")
    seen = set()
    for t in manifest.tiles:
        if "id" not in t or "frame" not in t:
            raise ValueError("each tile must have 'id' and 'frame'")
        if t["id"] in seen:
            raise ValueError(f"duplicate tile id: {t['id']}")
        seen.add(t["id"])
        f = t["frame"]
        for k in ("x", "y", "w", "h"):
            if k not in f or not isinstance(f[k], int):
                raise ValueError(f"tile {t['id']} frame.{k} must be int")
    if manifest.site is not None:
        ids: set[str] = set()
        for page in manifest.site.pages:
            pid = str(page.get("id"))
            route = str(page.get("route"))
            title = page.get("title")
            if not pid:
                raise ValueError("site.pages entries require an 'id'")
            if pid in ids:
                raise ValueError(f"duplicate site page id: {pid}")
            ids.add(pid)
            if not route.startswith("/"):
                raise ValueError(
                    f"site page '{pid}' route must start with '/': {route}"
                )
            if title is None:
                raise ValueError(f"site page '{pid}' missing title")
    if manifest.channels:
        channel_ids: set[str] = set()
        for ch in manifest.channels:
            if ch.id in channel_ids:
                raise ValueError(f"duplicate channel id: {ch.id}")
            channel_ids.add(ch.id)
            if ch.scope not in ALLOW:
                raise ValueError(f"channel '{ch.id}' has unknown scope '{ch.scope}'")
            if not ch.topic:
                raise ValueError(f"channel '{ch.id}' requires a topic")
    if manifest.ws_routes:
        for route in manifest.ws_routes:
            if not route.path.startswith("/"):
                raise ValueError(f"ws route path must start with '/': {route.path}")
            for channel_id in route.channels:
                if manifest.channels and channel_id not in {
                    c.id for c in manifest.channels
                }:
                    raise ValueError(
                        f"ws route '{route.path}' references unknown channel '{channel_id}'"
                    )


def schema() -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Layout Manifest",
        "type": "object",
        "required": ["kind", "version", "viewport", "grid", "tiles", "etag"],
        "properties": {
            "kind": {"const": "layout_manifest"},
            "version": {"type": "string"},
            "viewport": {
                "type": "object",
                "required": ["width", "height"],
                "properties": {
                    "width": {"type": "integer", "minimum": 0},
                    "height": {"type": "integer", "minimum": 0},
                },
            },
            "grid": {"type": "object"},
            "tiles": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["id", "role", "frame", "props"],
                    "properties": {
                        "id": {"type": "string"},
                        "role": {"type": "string"},
                        "frame": {
                            "type": "object",
                            "required": ["x", "y", "w", "h"],
                            "properties": {
                                "x": {"type": "integer"},
                                "y": {"type": "integer"},
                                "w": {"type": "integer"},
                                "h": {"type": "integer"},
                            },
                        },
                        "props": {"type": "object"},
                        "atom": {
                            "type": "object",
                            "properties": {
                                "module": {"type": "string"},
                                "export": {"type": "string"},
                                "version": {"type": "string"},
                                "defaults": {"type": "object"},
                            },
                        },
                    },
                },
            },
            "etag": {"type": "string"},
            "site": {
                "type": ["object", "null"],
                "properties": {
                    "pages": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["id", "route", "title"],
                            "properties": {
                                "id": {"type": "string"},
                                "route": {"type": "string"},
                                "title": {"type": "string"},
                                "slots": {"type": "array"},
                                "meta": {"type": "object"},
                            },
                        },
                    },
                    "active_page": {"type": ["string", "null"]},
                    "navigation": {"type": "object"},
                },
            },
            "channels": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["id", "scope", "topic"],
                    "properties": {
                        "id": {"type": "string"},
                        "scope": {"type": "string"},
                        "topic": {"type": "string"},
                        "description": {"type": "string"},
                        "payload_schema": {"type": "object"},
                        "meta": {"type": "object"},
                    },
                },
            },
            "ws_routes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["path"],
                    "properties": {
                        "path": {"type": "string"},
                        "channels": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "description": {"type": "string"},
                        "meta": {"type": "object"},
                    },
                },
            },
        },
        "additionalProperties": False,
    }


def _frame_map(manifest: Manifest) -> dict[str, Frame]:
    frames: dict[str, Frame] = {}
    for tile in manifest.tiles:
        tile_dict = dict(tile)
        frame = tile_dict.get("frame", {})
        frames[tile_dict["id"]] = Frame(
            x=int(frame.get("x", 0)),
            y=int(frame.get("y", 0)),
            w=int(frame.get("w", 0)),
            h=int(frame.get("h", 0)),
        )
    return frames


def diff(old: Manifest, new: Manifest, *, epsilon: int = 0) -> dict:
    old_frames = _frame_map(old)
    new_frames = _frame_map(new)
    geom = frame_diff(old_frames, new_frames, epsilon=epsilon)
    added = geom["added"]
    removed = geom["removed"]
    changed = geom["changed"]
    unchanged = geom["unchanged"]
    frames = {tid: new_frames[tid].__dict__ for tid in changed + added}
    return {
        "base_etag": old.etag,
        "etag": new.etag,
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged,
        "frames": frames,
    }


def apply_patch(base: Manifest, patch: Mapping[str, Any]) -> Manifest:
    base_d = to_dict(base)
    tiles = {t["id"]: dict(t) for t in base_d["tiles"]}
    for tid in patch.get("removed", []):
        tiles.pop(tid, None)
    for tid, fr in (patch.get("frames") or {}).items():
        if tid not in tiles:
            tiles[tid] = {
                "id": tid,
                "role": "",
                "props": {},
                "frame": {"x": 0, "y": 0, "w": 0, "h": 0},
            }
        tiles[tid]["frame"] = {k: int(fr[k]) for k in ("x", "y", "w", "h")}
    base_d["tiles"] = sorted(tiles.values(), key=lambda t: t["id"])
    base_d["etag"] = patch.get("etag", base.etag)
    return from_dict(base_d)


def compute_etag(obj: Mapping[str, Any]) -> str:
    return etag_of(obj)


def validate_manifest(manifest: Manifest) -> None:
    validate(manifest)


def sort_tiles(manifest: Manifest) -> Manifest:
    data = to_dict(manifest)
    data["tiles"] = sorted(data["tiles"], key=lambda t: t.get("id", ""))
    return from_dict(data)


def to_plain_dict(manifest: Manifest) -> dict:
    return to_dict(manifest)


def from_plain_dict(data: Mapping[str, Any]) -> Manifest:
    return from_dict(data)


def diff_manifests(old: Manifest, new: Manifest, *, epsilon: int = 0) -> dict:
    return diff(old, new, epsilon=epsilon)


def make_patch(old: Manifest, new: Manifest, *, epsilon: int = 0) -> dict:
    return diff(old, new, epsilon=epsilon)
