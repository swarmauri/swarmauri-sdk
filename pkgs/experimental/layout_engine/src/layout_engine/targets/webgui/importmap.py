from __future__ import annotations
import json
from ...mfe.default import ImportMapBuilder, RemoteRegistry


def import_map_json(
    registry: RemoteRegistry, *, include_integrity: bool = True
) -> dict:
    return ImportMapBuilder().build(registry, include_integrity=include_integrity)


def import_map_text(
    registry: RemoteRegistry,
    *,
    include_integrity: bool = True,
    indent: int | None = None,
) -> str:
    return json.dumps(
        import_map_json(registry, include_integrity=include_integrity),
        indent=indent,
        sort_keys=True,
    )
