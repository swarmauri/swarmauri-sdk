"""High-level manifest helpers for layout-engine atoms."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from layout_engine import LayoutCompiler, ManifestBuilder, TileSpec, Viewport
from layout_engine.core.size import Size
from layout_engine.grid.spec import GridSpec, GridTile, GridTrack
from layout_engine.structure import Table as LayoutTable

from .catalog import build_registry as build_catalog_registry

_DEFAULT_COLUMNS = 2


@dataclass(slots=True)
class Tile:
    """Declarative tile configuration for quick manifest helpers."""

    id: str
    role: str
    props: Mapping[str, Any] | None = None
    span: int | str = "auto"
    row_span: int = 1

    def to_spec(self) -> TileSpec:
        return TileSpec(
            id=self.id,
            role=self.role,
            props=dict(self.props or {}),
        )


def tile(
    id: str,
    role: str,
    *,
    props: Mapping[str, Any] | None = None,
    span: int | str = "auto",
    row_span: int = 1,
) -> Tile:
    """Convenience factory matching :class:`Tile` signature."""

    return Tile(id=id, role=role, props=props, span=span, row_span=row_span)


def create_registry(
    *,
    catalog: str = "vue",
    extra_presets: Iterable[Mapping[str, Any]] | None = None,
    overrides: Mapping[str, Mapping[str, Any]] | None = None,
):
    """Return an :class:`AtomRegistry` primed with SwarmaKit presets."""

    return build_catalog_registry(
        catalog,
        extra_presets=extra_presets,
        overrides=overrides,
    )


def quick_manifest(
    tiles: Sequence[Tile | Mapping[str, Any]],
    *,
    catalog: str = "vue",
    registry=None,
    columns: int = _DEFAULT_COLUMNS,
    row_height: int = 220,
    viewport: Viewport | tuple[int, int] | None = None,
    channels: Sequence[Mapping[str, Any]] | None = None,
    ws_routes: Sequence[Mapping[str, Any]] | None = None,
    version: str = "2025.10",
):
    """Build a manifest using the SwarmaKit registry defaults."""

    registry = registry or create_registry(catalog=catalog)
    manifest, _ = build_manifest_from_tiles(
        tiles,
        registry=registry,
        columns=columns,
        row_height=row_height,
        viewport=viewport,
        channels=channels,
        ws_routes=ws_routes,
        version=version,
    )
    return manifest


def build_manifest_from_tiles(
    tiles: Sequence[Tile | Mapping[str, Any]],
    *,
    registry,
    columns: int = _DEFAULT_COLUMNS,
    row_height: int = 220,
    viewport: Viewport | tuple[int, int] | None = None,
    channels: Sequence[Mapping[str, Any]] | None = None,
    ws_routes: Sequence[Mapping[str, Any]] | None = None,
    version: str = "2025.10",
):
    """Build a :class:`Manifest` and return it alongside the view model."""

    columns = max(1, int(columns))
    grid = _build_grid(columns, row_height)

    tile_entries: list[Tile] = [_coerce_tile(t) for t in tiles]
    placements = _auto_place(tile_entries, columns)

    compiler = LayoutCompiler()
    vp = _viewport_from(viewport, columns, placements, row_height)
    frames = compiler.frames(grid, vp, placements)

    specs = [entry.to_spec() for entry in tile_entries]
    view_model = compiler.view_model(
        grid,
        vp,
        frames,
        specs,
        atoms_registry=registry,
        channels=channels,
        ws_routes=ws_routes,
    )

    manifest = ManifestBuilder().build(view_model, version=version)
    _enrich_atom_metadata(manifest, registry)
    return manifest, view_model


def quick_manifest_from_table(
    layout: LayoutTable,
    tiles: Sequence[Tile | Mapping[str, Any]],
    *,
    catalog: str = "vue",
    registry=None,
    row_height: int = 220,
    viewport: Viewport | tuple[int, int] | None = None,
    channels: Sequence[Mapping[str, Any]] | None = None,
    ws_routes: Sequence[Mapping[str, Any]] | None = None,
    version: str = "2025.10",
):
    """Build a manifest from a structure.Table definition."""

    registry = registry or create_registry(catalog=catalog)
    manifest, _ = build_manifest_from_table(
        layout,
        tiles,
        registry=registry,
        row_height=row_height,
        viewport=viewport,
        channels=channels,
        ws_routes=ws_routes,
        version=version,
    )
    return manifest


def build_manifest_from_table(
    layout: LayoutTable,
    tiles: Sequence[Tile | Mapping[str, Any]],
    *,
    registry,
    row_height: int = 220,
    viewport: Viewport | tuple[int, int] | None = None,
    channels: Sequence[Mapping[str, Any]] | None = None,
    ws_routes: Sequence[Mapping[str, Any]] | None = None,
    version: str = "2025.10",
):
    """Build a manifest from a Table/Row/Col structure."""

    compiler = LayoutCompiler()
    vp = _ensure_viewport(viewport)
    grid, placements, frames = compiler.frames_from_structure(
        layout,
        vp,
        row_height=row_height,
    )

    specs = [_coerce_tile(t).to_spec() for t in tiles]
    view_model = compiler.view_model(
        grid,
        vp,
        frames,
        specs,
        atoms_registry=registry,
        channels=channels,
        ws_routes=ws_routes,
    )

    manifest = ManifestBuilder().build(view_model, version=version)
    _enrich_atom_metadata(manifest, registry)
    return manifest, view_model


def _coerce_tile(candidate: Tile | Mapping[str, Any]) -> Tile:
    if isinstance(candidate, Tile):
        return candidate
    data = dict(candidate)
    return Tile(
        id=data.pop("id"),
        role=data.pop("role"),
        props=data.pop("props", None),
        span=data.pop("span", "auto"),
        row_span=data.pop("row_span", 1),
    )


def _build_grid(columns: int, row_height: int) -> GridSpec:
    tracks = [GridTrack(size=Size(1, "fr")) for _ in range(columns)]
    return GridSpec(
        columns=tracks,
        row_height=row_height,
        tokens={"columns": f"sgd:columns:{columns}"},
    )


def _auto_place(tiles: Sequence[Tile], columns: int) -> list[GridTile]:
    placements: list[GridTile] = []
    col = 0
    row = 0
    for entry in tiles:
        span = _span_value(entry.span, columns)
        if span > columns:
            span = columns
        if col + span > columns:
            col = 0
            row += 1
        placements.append(
            GridTile(
                tile_id=entry.id,
                col=col,
                row=row,
                col_span=span,
                row_span=max(1, entry.row_span),
            )
        )
        col += span
        if col >= columns:
            col = 0
            row += 1
    return placements


def _span_value(span: int | str, columns: int) -> int:
    if isinstance(span, int):
        return max(1, span)
    mapping = {
        "full": columns,
        "half": max(1, columns // 2) if columns > 1 else 1,
        "third": max(1, columns // 3),
        "auto": 1,
    }
    return mapping.get(span, 1)


def _viewport_from(
    viewport: Viewport | tuple[int, int] | None,
    columns: int,
    placements: Sequence[GridTile],
    row_height: int,
) -> Viewport:
    if isinstance(viewport, Viewport):
        return viewport
    if isinstance(viewport, tuple):
        width, height = viewport
        return Viewport(width=width, height=height)
    rows = 1
    if placements:
        rows = max(placement.row + placement.row_span for placement in placements)
    width = max(columns * 640, 640)
    height = max(rows * row_height, row_height)
    return Viewport(width=width, height=height)


def _ensure_viewport(viewport: Viewport | tuple[int, int] | None) -> Viewport:
    if isinstance(viewport, Viewport):
        return viewport
    if isinstance(viewport, tuple):
        width, height = viewport
        return Viewport(width=width, height=height)
    return Viewport(width=1280, height=960)


def _enrich_atom_metadata(manifest, registry) -> None:
    tiles = manifest.tiles if isinstance(manifest.tiles, list) else list(manifest.tiles)
    for tile in tiles:
        if not isinstance(tile, dict):
            continue
        try:
            spec = registry.get(tile["role"])
        except Exception:  # noqa: BLE001
            continue
        atom_data = dict(tile.get("atom") or {})
        atom_data.setdefault("role", spec.role)
        atom_data.setdefault("module", spec.module)
        atom_data.setdefault("export", spec.export)
        atom_data.setdefault("version", spec.version)
        if spec.defaults and not atom_data.get("defaults"):
            atom_data["defaults"] = dict(spec.defaults)
        if getattr(spec, "family", None) and not atom_data.get("family"):
            atom_data["family"] = spec.family
        if getattr(spec, "framework", None) and not atom_data.get("framework"):
            atom_data["framework"] = spec.framework
        if getattr(spec, "package", None) and not atom_data.get("package"):
            atom_data["package"] = spec.package
        tokens = getattr(spec, "tokens", None)
        if tokens and not atom_data.get("tokens"):
            atom_data["tokens"] = dict(tokens)
        registry_meta = getattr(spec, "registry", None)
        if registry_meta and not atom_data.get("registry"):
            atom_data["registry"] = dict(registry_meta)
        tile["atom"] = atom_data


__all__ = [
    "Tile",
    "tile",
    "create_registry",
    "quick_manifest",
    "build_manifest_from_tiles",
]
