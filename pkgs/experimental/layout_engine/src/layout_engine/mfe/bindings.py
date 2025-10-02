from __future__ import annotations
from typing import Mapping, Any
import json
from .spec import Remote

def to_dict(r: Remote) -> dict:
    return {
        "id": r.id, "framework": r.framework, "entry": r.entry,
        "exposed": r.exposed, "integrity": r.integrity,
    }

def from_dict(obj: Mapping[str, Any]) -> Remote:
    return Remote(
        id=str(obj["id"]),
        framework=str(obj["framework"]),  # validated in Remote.__post_init__
        entry=str(obj["entry"]),
        exposed=str(obj["exposed"]),
        integrity=(str(obj["integrity"]) if obj.get("integrity") else None),
    )

def registry_to_dict(registry) -> dict[str, dict]:
    return registry.to_dict()

def registry_from_dict(registry, data: Mapping[str, Mapping[str, Any]]) -> None:
    registry.update_from_dict(data)  # upsert

# -------- Import map helpers --------

def to_import_map(registry, *, extra_imports: dict[str,str] | None = None,
                  scopes: dict[str, dict[str,str]] | None = None) -> dict:
    imports = {rid: r["entry"] for rid, r in registry_to_dict(registry).items()}
    if extra_imports:
        imports.update(extra_imports)
    imap = {"imports": imports}
    if scopes:
        imap["scopes"] = scopes
    return imap

def to_import_map_json(registry, *, extra_imports: dict[str,str] | None = None,
                       scopes: dict[str, dict[str,str]] | None = None, indent: int | None = None) -> str:
    imap = to_import_map(registry, extra_imports=extra_imports, scopes=scopes)
    return json.dumps(imap, indent=indent, sort_keys=True)

def script_tag(import_map: dict, *, indent: int | None = 2) -> str:
    js = json.dumps(import_map, indent=indent, sort_keys=True)
    return f'<script type="importmap">{js}</script>'

def modulepreload_html(import_map: Mapping[str, Any]) -> str:
    """Return a string with <link rel="modulepreload"> tags for top-level imports."""
    imports = list(import_map.get("imports", {}).values())
    return "\n".join(f'<link rel="modulepreload" href="{href}">' for href in imports)
