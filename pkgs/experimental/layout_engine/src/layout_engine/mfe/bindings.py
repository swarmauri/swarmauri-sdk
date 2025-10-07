from __future__ import annotations

import json
from typing import Any, Mapping

from .spec import Remote


def to_dict(remote: Remote) -> dict:
    if hasattr(remote, "model_dump"):
        return remote.model_dump()
    if hasattr(remote, "dict"):
        return remote.dict()
    return {
        "id": remote.id,
        "framework": remote.framework,
        "entry": remote.entry,
        "exposed": remote.exposed,
        "integrity": remote.integrity,
    }


def from_dict(obj: Mapping[str, Any]) -> Remote:
    return Remote(
        id=str(obj["id"]),
        framework=str(obj["framework"]),
        entry=str(obj["entry"]),
        exposed=str(obj.get("exposed", "./App")),
        integrity=(str(obj["integrity"]) if obj.get("integrity") else None),
    )


def registry_to_dict(registry) -> dict[str, dict]:
    if hasattr(registry, "to_dict"):
        return registry.to_dict()
    return {}


def registry_from_dict(registry, data: Mapping[str, Mapping[str, Any]]) -> None:
    if hasattr(registry, "update_from_dict"):
        registry.update_from_dict(data)


def to_import_map(
    registry,
    *,
    extra_imports: dict[str, str] | None = None,
    scopes: dict[str, dict[str, str]] | None = None,
) -> dict:
    imports = {rid: info["entry"] for rid, info in registry_to_dict(registry).items()}
    if extra_imports:
        imports.update(extra_imports)
    out = {"imports": imports}
    if scopes:
        out["scopes"] = scopes
    return out


def to_import_map_json(
    registry,
    *,
    extra_imports: dict[str, str] | None = None,
    scopes: dict[str, dict[str, str]] | None = None,
    indent: int | None = None,
) -> str:
    imap = to_import_map(registry, extra_imports=extra_imports, scopes=scopes)
    return json.dumps(imap, indent=indent, sort_keys=True)


def script_tag(import_map: Mapping[str, Any], *, indent: int | None = 2) -> str:
    js = json.dumps(import_map, indent=indent, sort_keys=True)
    return f'<script type="importmap">{js}</script>'


def modulepreload_html(import_map: Mapping[str, Any]) -> str:
    imports = list(import_map.get("imports", {}).values())
    return "\n".join(f'<link rel="modulepreload" href="{href}">' for href in imports)
