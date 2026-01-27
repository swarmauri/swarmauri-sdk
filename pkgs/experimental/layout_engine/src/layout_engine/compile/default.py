from __future__ import annotations
from typing import Any, Iterable, Literal, Mapping, Sequence

from ..core.viewport import Viewport
from ..core.frame import Frame
from ..grid.default import ExplicitGridResolver
from ..grid.base import IGridResolver
from ..grid.spec import GridSpec, GridTile
from ..tiles.spec import TileSpec
from ..atoms.base import IAtomRegistry
from ..design.tokens import layout_tokens_from_grid

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
    def frames(
        self, gs: GridSpec, vp: Viewport, placements: list[GridTile]
    ) -> dict[str, Frame]:
        """Compile placements to pixel frames using the configured grid resolver."""
        return self._resolver.frames(gs, vp, placements)

    # ---- Authoring DSL helpers (structure -> grid -> frames) ----
    def frames_from_structure(self, tbl, vp: Viewport, *, row_height: int = 180):
        """Compile Table/Row/Col/Block to (GridSpec, placements, Frames).

        Notes: We import structure lazily to avoid import cycles for users who don't use the DSL.
        """
        from ..structure.default import (
            GridBuilder,
        )  # local import to avoid hard dep if unused

        gb = GridBuilder(row_height=row_height)
        gs, placements = gb.to_grid(tbl, vp)
        return gs, placements, self.frames(gs, vp, placements)

    # ---- View-model helpers (for manifest building) ----
    def view_model(
        self,
        gs: GridSpec,
        vp: Viewport,
        frames_map: dict[str, Frame],
        tiles: Iterable[TileSpec],
        atoms_registry: IAtomRegistry | None = None,
        *,
        channels: Sequence[Mapping[str, object]] | None = None,
        ws_routes: Sequence[Mapping[str, object]] | None = None,
    ) -> dict:
        """Build a minimal view-model dict expected by `manifest.build_manifest`.

        - Adds viewport, serialized grid, and a tile list with frames.
        - Optionally includes atom mapping (module/export/version/defaults) from a registry.
        """
        from ..grid.bindings import gridspec_to_dict

        layout_bundle = layout_tokens_from_grid(gs)
        layout_meta = layout_bundle.get("meta", {})
        swarma_layout = layout_bundle.get("swarma_props", {})

        def _merge_missing(target: dict, addition: Mapping[str, Any]) -> None:
            for key, value in addition.items():
                if isinstance(value, Mapping):
                    nested = target.setdefault(key, {})
                    if isinstance(nested, Mapping):
                        _merge_missing(nested, value)
                    else:
                        target[key] = dict(value)
                else:
                    target.setdefault(key, value)

        tiles_payload: list[dict] = []
        for t in tiles:
            if t.id not in frames_map:
                # skip tiles that have no placement/frame
                continue
            frame = frames_map[t.id].to_dict()
            base_props = dict(getattr(t, "props", {}))
            entry = {
                "id": t.id,
                "role": t.role,
                "props": base_props,
                "frame": frame,
            }
            if atoms_registry is not None:
                try:
                    atom = atoms_registry.get(t.role)  # type: ignore[attr-defined]
                except Exception:
                    # unknown role; leave atom mapping absent
                    pass
                else:
                    defaults = dict(getattr(atom, "defaults", {}))
                    merged_props = dict(defaults)
                    merged_props.update(base_props)
                    entry["atom"] = {
                        "role": atom.role,
                        "module": atom.module,
                        "export": atom.export,
                        "version": atom.version,
                        "defaults": defaults,
                    }
                    if getattr(atom, "framework", None):
                        entry["atom"]["framework"] = atom.framework
                    if getattr(atom, "package", None):
                        entry["atom"]["package"] = atom.package
                    if getattr(atom, "family", None):
                        entry["atom"]["family"] = atom.family
                    if getattr(atom, "tokens", None):
                        tokens = dict(getattr(atom, "tokens", {}))
                        if tokens:
                            entry["atom"]["tokens"] = tokens
                    if getattr(atom, "registry", None):
                        registry_meta = dict(getattr(atom, "registry", {}))
                        if registry_meta:
                            entry["atom"]["registry"] = registry_meta
                    # Defaults merge underneath author-specified props
                    entry["props"] = merged_props
                    if swarma_layout and entry["atom"].get("family") == "swarmakit":
                        _merge_missing(entry["props"], swarma_layout)
            tiles_payload.append(entry)

        vm = {
            "viewport": {"width": vp.width, "height": vp.height},
            "grid": gridspec_to_dict(gs),
            "tiles": tiles_payload,
        }
        if getattr(gs, "tokens", None):
            vm.setdefault("meta", {})["grid_tokens"] = dict(gs.tokens)
        if getattr(gs, "baseline_unit", None) is not None:
            vm.setdefault("meta", {}).setdefault("grid", {})["baseline_unit"] = int(
                gs.baseline_unit
            )
        if layout_meta:
            vm.setdefault("meta", {}).setdefault("layout", {}).update(layout_meta)
        if atoms_registry is not None:
            try:
                revision = getattr(atoms_registry, "revision", None)
            except Exception:
                revision = None
            if revision is not None:
                vm.setdefault("meta", {}).setdefault("atoms", {})["revision"] = revision
        if channels:
            vm["channels"] = [dict(ch) for ch in channels]
        if ws_routes:
            vm["ws_routes"] = [dict(route) for route in ws_routes]
        return vm

    def view_model_from_structure(
        self,
        tbl,
        vp: Viewport,
        tiles: Iterable[TileSpec],
        *,
        row_height: int = 180,
        atoms_registry: IAtomRegistry | None = None,
        channels: Sequence[Mapping[str, object]] | None = None,
        ws_routes: Sequence[Mapping[str, object]] | None = None,
    ) -> dict:
        """End-to-end convenience: Table/Row/Col/Block → Frames → view-model dict."""
        gs, placements, frames_map = self.frames_from_structure(
            tbl, vp, row_height=row_height
        )
        return self.view_model(
            gs,
            vp,
            frames_map,
            tiles,
            atoms_registry=atoms_registry,
            channels=channels,
            ws_routes=ws_routes,
        )

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
    kind: Literal["added", "removed", "changed", "unchanged"]

    # --- context manager support ---
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False
