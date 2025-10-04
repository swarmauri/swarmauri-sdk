from pydantic import BaseModel, Field, validator
from __future__ import annotations
from pydantic import BaseModel, Field, validator, field, replace
from typing import Optional, Mapping, Any
import re

_ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_:-]{1,63}$")
_ROLE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_:-]{1,63}$")

def validate_tile_id(tile_id: str) -> str:
    if not _ID_RE.match(tile_id):
        raise ValueError(f"invalid tile id '{tile_id}' (allowed: [A-Za-z][A-Za-z0-9_:-] 2..64)")
    return tile_id

def validate_role(role: str) -> str:
    if not _ROLE_RE.match(role):
        raise ValueError(f"invalid role '{role}' (allowed: [A-Za-z][A-Za-z0-9_:-] 2..64)")
    return role

class TileSpec(BaseModel):
    """Declarative spec for a tile's identity, role, and constraints.

    Fields
    ------
    id:        unique identifier for the tile (stable across reflows)
    role:      semantic role (e.g., 'kpi', 'table', 'timeseries', ...) used to resolve the UI component
    min_w/h:   minimal pixel footprint
    max_w/h:   optional clamps (>= min)
    aspect:    optional width/height ratio hint (purely informative at this layer)
    props:     authoring-time properties (merged later with component defaults)
    meta:      free-form metadata (owner, tags, testids, etc.)
    """
    id: str
    role: str = "generic"
    min_w: int = 160
    min_h: int = 120
    max_w: Optional[int] = None
    max_h: Optional[int] = None
    aspect: Optional[float] = None
    props: Mapping[str, Any] = field(default_factory=dict)
    meta: Mapping[str, Any] = field(default_factory=dict)

