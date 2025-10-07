from __future__ import annotations
from typing import Mapping, Any
from .spec import TileSpec
from .default import Tile

# ---- Spec JSON (de)serialization ----


def to_dict(spec: TileSpec) -> dict:
    if hasattr(spec, "model_dump"):
        return spec.model_dump()
    if hasattr(spec, "dict"):
        return spec.dict()
    return dict(spec)


def from_dict(obj: Mapping[str, Any]) -> TileSpec:
    return TileSpec(
        id=str(obj["id"]),
        role=str(obj.get("role", "generic")),
        min_w=int(obj.get("min_w", 160)),
        min_h=int(obj.get("min_h", 120)),
        max_w=(int(obj["max_w"]) if obj.get("max_w") is not None else None),
        max_h=(int(obj["max_h"]) if obj.get("max_h") is not None else None),
        aspect=(float(obj["aspect"]) if obj.get("aspect") is not None else None),
        props=dict(obj.get("props", {})),
        meta=dict(obj.get("meta", {})),
    )


# ---- Tile JSON (de)serialization ----


def tile_to_dict(t: Tile) -> dict:
    return {"spec": to_dict(t.spec)}


def tile_from_dict(d: Mapping[str, Any]) -> Tile:
    return Tile(spec=from_dict(d["spec"]))
