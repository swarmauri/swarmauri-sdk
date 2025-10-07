from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping, Any
from .spec import TileSpec


@dataclass(frozen=True)
class Tile:
    spec: TileSpec

    # convenience property passthroughs
    @property
    def id(self) -> str:
        return self.spec.id

    @property
    def role(self) -> str:
        return self.spec.role

    def to_dict(self) -> Mapping[str, Any]:
        s = self.spec
        return {
            "id": s.id,
            "role": s.role,
            "constraints": {
                "min_w": s.min_w,
                "min_h": s.min_h,
                "max_w": s.max_w,
                "max_h": s.max_h,
                "aspect": s.aspect,
            },
            "props": dict(s.props),
            "meta": dict(s.meta),
        }
