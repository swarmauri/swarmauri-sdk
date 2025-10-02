from __future__ import annotations
from typing import Iterable
from .spec import Remote
from .default import RemoteRegistry, ImportMapBuilder
from .bindings import to_import_map_json, script_tag, modulepreload_html

def remote(**kwargs) -> Remote:
    return Remote(**kwargs)

def remotes(*r: Remote) -> RemoteRegistry:
    return RemoteRegistry(r)

def build_import_map(registry: RemoteRegistry, *, extra_imports: dict[str,str] | None = None,
                     scopes: dict[str, dict[str,str]] | None = None) -> dict:
    return ImportMapBuilder().build(registry, extra_imports=extra_imports, scopes=scopes)

def import_map_script(registry: RemoteRegistry, *, extra_imports: dict[str,str] | None = None,
                      scopes: dict[str, dict[str,str]] | None = None, indent: int | None = None) -> str:
    imap = build_import_map(registry, extra_imports=extra_imports, scopes=scopes)
    return script_tag(imap, indent=indent)

def modulepreload_links(registry: RemoteRegistry, *, extra_imports: dict[str,str] | None = None,
                        scopes: dict[str, dict[str,str]] | None = None) -> str:
    imap = build_import_map(registry, extra_imports=extra_imports, scopes=scopes)
    return modulepreload_html(imap)
