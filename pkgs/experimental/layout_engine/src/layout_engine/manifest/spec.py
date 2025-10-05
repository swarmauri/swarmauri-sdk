from pydantic import BaseModel, Field, validator
from __future__ import annotations
from pydantic import BaseModel, Field, validator
from typing import Any, Mapping, Sequence

class Manifest(BaseModel):
    """Canonical page manifest.

    Fields:
      - kind:            literal "layout_manifest"
      - version:         semver-ish string (e.g., "2025.10")
      - viewport:        {"width": int, "height": int}
      - grid:            mapping with row_height/gaps/columns (binding-level shape)
      - tiles:           list of tile payloads:
                         { id: str, role: str, frame: {x,y,w,h}, props: {...}, component?: {...} }
      - etag:            content hash for cache/patch validation
    """
    kind: str
    version: str
    viewport: Mapping[str, Any]
    grid: Mapping[str, Any]
    tiles: list[Mapping[str, Any]]
    etag: str
