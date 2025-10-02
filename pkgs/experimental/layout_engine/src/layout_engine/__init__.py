
"""layout_engine — Grid-first, framework-agnostic layout & manifest toolkit.

This package provides:
  • Core primitives: Size/Viewport/Frame
  • Authoring DSL: table/row/col/block → explicit grid
  • Grid runtime: deterministic px/%/fr resolution with breakpoints
  • Compile: explicit grid → frames (+ view-model helpers)
  • Manifest: stable, cacheable JSON contract (+ diff/patch)
  • Events: validated envelopes + in-proc router/bus
  • Site: routes/pages/slots + resolution
  • MFE: remote registry + import-map
  • Targets: WebGUI SSR shell helpers and Media exporters (HTML/SVG/PDF/Code)

Ergonomics:
  • quick_view_model_from_table(...) — authoring DSL → view-model (with optional components registry)
  • quick_manifest_from_table(...)  — authoring DSL → manifest
"""

__version__ = "0.1.0"

# ---- Core ----
from .core.size import Size, SizeToken, DEFAULT_TOKEN_WEIGHTS
from .core.viewport import Viewport
from .core.frame import Frame

# ---- Tiles ----
from .tiles import TileSpec, Tile, tile_spec, make_tile

# ---- Components ----
from .components import (
    ComponentSpec, ComponentRegistry, define_component, use_component, apply_defaults
)

# ---- Grid ----
from .grid import (
    GridTrack, GridSpec, GridTile,
    ExplicitGridResolver,
    make_gridspec, place, gridspec_from_tokens, breakpoint, breakpoints,
)

# ---- Structure (authoring DSL) ----
from .structure import (
    Block, Column, Row, Table,
    GridBuilder, validate_table,
    block, col, row, table, build_grid, gridify,
)

# ---- Compile ----
from .compile import (
    LayoutCompiler,
    frame_map_from_placements, frame_diff, frames_almost_equal,
    ordering_by_topleft, ordering_diff,
)

# ---- Manifest ----
from .manifest import (
    Manifest, TileEntry, ManifestBuilder, build_manifest,
    manifest_to_json, manifest_from_json,
    compute_etag, validate_manifest, sort_tiles, to_plain_dict, from_plain_dict,
    diff_manifests, make_patch, apply_patch,
)

# ---- Events ----
from .events import (
    EventEnvelope, ValidationError,
    validate_envelope, is_allowed, allowed_types_for, route_topic,
    InProcEventBus, EventRouter,
    utc_now_iso, make_ack, make_error,
)

# ---- Site (routing) ----
from .site import (
    SlotSpec, PageSpec, SiteSpec, RouteMatch,
    compile_route_pattern, normalize_base_path,
    SiteIndex, resolve_path, validate_site, build_page_context, bind_page_builder,
)

# ---- MFE (remote registry & import-map) ----
from .mfe import (
    Remote, Framework, RemoteRegistry, ImportMapBuilder,
    remote, remotes, build_import_map, compose_import_maps,
    import_map_json,
)

# ---- Targets ----
from .targets import (
    RenderResult,
    HtmlShell, SiteRouter, import_map_json as webgui_import_map_json,
    HtmlExporter, SvgExporter, PdfExporter, CodeExporter,
)

# ---------------- Convenience helpers ----------------

def quick_view_model_from_table(tbl, vp: Viewport, tiles, *, row_height: int = 180, components_registry=None) -> dict:
    """Authoring DSL → (Frames →) view-model suitable for manifest building.

    Args:
      tbl: structure.Table
      vp:  core.Viewport
      tiles: Iterable[tiles.TileSpec]
      row_height: baseline grid row height (px)
      components_registry: optional components registry for role→module mapping

    Returns:
      dict view-model with keys: { viewport, grid, tiles }
    """
    compiler = LayoutCompiler()
    return compiler.view_model_from_structure(
        tbl, vp, tiles,
        row_height=row_height,
        components_registry=components_registry
    )

def quick_manifest_from_table(tbl, vp: Viewport, tiles, *, row_height: int = 180, components_registry=None, version: str = "2025.10") -> Manifest:
    """Authoring DSL → manifest (one call convenience)."""
    vm = quick_view_model_from_table(
        tbl, vp, tiles,
        row_height=row_height,
        components_registry=components_registry
    )
    return build_manifest(vm, version=version)

__all__ = [
    "__version__",
    # core
    "Size","SizeToken","DEFAULT_TOKEN_WEIGHTS","Viewport","Frame",
    # tiles
    "TileSpec","Tile","tile_spec","make_tile",
    # components
    "ComponentSpec","ComponentRegistry","define_component","use_component","apply_defaults",
    # grid
    "GridTrack","GridSpec","GridTile","ExplicitGridResolver",
    "make_gridspec","place","gridspec_from_tokens","breakpoint","breakpoints",
    # structure
    "Block","Column","Row","Table","GridBuilder","validate_table","block","col","row","table","build_grid","gridify",
    # compile
    "LayoutCompiler","frame_map_from_placements","frame_diff","frames_almost_equal","ordering_by_topleft","ordering_diff",
    # manifest
    "Manifest","TileEntry","ManifestBuilder","build_manifest","manifest_to_json","manifest_from_json",
    "compute_etag","validate_manifest","sort_tiles","to_plain_dict","from_plain_dict","diff_manifests","make_patch","apply_patch",
    # events
    "EventEnvelope","ValidationError","validate_envelope","is_allowed","allowed_types_for","route_topic","InProcEventBus","EventRouter","utc_now_iso","make_ack","make_error",
    # site
    "SlotSpec","PageSpec","SiteSpec","RouteMatch","compile_route_pattern","normalize_base_path","SiteIndex","resolve_path","validate_site","build_page_context","bind_page_builder",
    # mfe
    "Remote","Framework","RemoteRegistry","ImportMapBuilder","remote","remotes","build_import_map","compose_import_maps","import_map_json",
    # targets
    "RenderResult","HtmlShell","SiteRouter","webgui_import_map_json","HtmlExporter","SvgExporter","PdfExporter","CodeExporter",
    # helpers
    "quick_view_model_from_table","quick_manifest_from_table",
]
