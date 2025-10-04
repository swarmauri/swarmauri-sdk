from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Literal

from ..core.viewport import Viewport
from ..core.frame import Frame
from ..grid.default import ExplicitGridResolver
from ..grid.base import IGridResolver
from ..grid.spec import GridSpec, GridTile
from ..tiles.spec import TileSpec

# --------- Core compiler ---------

class LayoutCompiler:
    """High-level compiler utilities around the explicit grid runtime.

    Responsibilities:
    - Convert an explicit GridSpec + GridTile placements into pixel Frames.
    - (Optional) Compile from the authoring DSL (Table/Row/Col/Block) to explicit grid, then to Frames.
    - (Optional) Assemble a framework-agnostic view-model consumable by the manifest builder.
    """
    def __init__(self, resolver: IGridResolver | None = None) -> None:
        self._resolver: IGridResolver = resolver or ExplicitGridResolver()

    # ---- Core API ----
    def frames(self, gs: GridSpec, vp: Viewport, placements: list[GridTile]) -> dict[str, Frame]:
        """Compile placements to pixel frames using the configured grid resolver."""
        return self._resolver.frames(gs, vp, placements)

    # ---- Authoring DSL helpers (structure -> grid -> frames) ----
    def frames_from_structure(self, tbl, vp: Viewport, *, row_height: int = 180):
        """Compile Table/Row/Col/Block to (GridSpec, placements, Frames).

        Notes: We import structure lazily to avoid import cycles for users who don't use the DSL.
        """
        from ..structure.default import GridBuilder  # local import to avoid hard dep if unused
        gb = GridBuilder(row_height=row_height)
        gs, placements = gb.to_grid(tbl, vp)
        return gs, placements, self.frames(gs, vp, placements)

    # ---- View-model helpers (for manifest building) ----
    def view_model(self,
                   gs: GridSpec,
                   vp: Viewport,
                   frames_map: dict[str, Frame],
                   tiles: Iterable[TileSpec],
                   components_registry: "IComponentRegistry|None" = None) -> dict:
        """Build a minimal view-model dict expected by `manifest.build_manifest`.

        - Adds viewport, serialized grid, and a tile list with frames.
        - Optionally includes component mapping (module/export/version/defaults) from a registry.
        """
        from ..grid.bindings import gridspec_to_dict
        tiles_payload: list[dict] = []
        for t in tiles:
            if t.id not in frames_map:
                # skip tiles that have no placement/frame
                continue
            frame = frames_map[t.id].to_dict()
            entry = {
                "id": t.id,
                "role": t.role,
                "props": {},   # caller can merge defaults downstream if desired
                "frame": frame,
            }
            if components_registry is not None:
                try:
                    comp = components_registry.get(t.role)  # type: ignore[attr-defined]
                    entry["component"] = {
                        "module": comp.module,
                        "export": comp.export,
                        "version": comp.version,
                        "defaults": dict(comp.defaults),
                    }
                    # By default, adopt defaults as props (can be overridden later)
                    entry["props"] = dict(comp.defaults)
                except Exception:
                    # unknown role; leave component mapping absent
                    pass
            tiles_payload.append(entry)

        vm = {
            "viewport": {"width": vp.width, "height": vp.height},
            "grid": gridspec_to_dict(gs),
            "tiles": tiles_payload,
        }
        return vm

    def view_model_from_structure(self,
                                  tbl,
                                  vp: Viewport,
                                  tiles: Iterable[TileSpec],
                                  *,
                                  row_height: int = 180,
                                  components_registry: "IComponentRegistry|None" = None) -> dict:
        """End-to-end convenience: Table/Row/Col/Block → Frames → view-model dict."""
        gs, placements, frames_map = self.frames_from_structure(tbl, vp, row_height=row_height)
        return self.view_model(gs, vp, frames_map, tiles, components_registry=components_registry)

# --------- Standalone helpers (pure functions) ---------

    # --- context manager support ---
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        return False

class FrameChange:
    tile_id: str
    before: Frame | None
    after: Frame | None
    kind: Literal["added","removed","changed","unchanged"]

    # --- context manager support ---
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        return False
