from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Tuple

from ..authoring.widgets import _Base as _WidgetBase
from ..components import ComponentRegistry, ComponentSpec
from ..contrib.presets import DEFAULT_ATOMS
from ..core.size import SizeToken
from ..tiles import tile_spec as _tile_spec
from .. import (
    block as d_block,
    col as d_col,
    row as d_row,
    table as d_table,
    LayoutCompiler,
    Viewport,
    build_manifest,
    HtmlShell,
)


@dataclass(frozen=True)
class ColD:
    size: str
    items: Tuple[_WidgetBase, ...]


@dataclass(frozen=True)
class RowD:
    height_rows: int
    cols: Tuple[ColD, ...]


@dataclass(frozen=True)
class TableD:
    rows: Tuple[RowD, ...]
    gap_x: int = 12
    gap_y: int = 12


@dataclass(frozen=True)
class PageD:
    route: str
    title: str
    table: TableD


@dataclass(frozen=True)
class SiteD:
    base_path: str = "/"
    pages: Tuple[PageD, ...] = ()


def _build_registry(
    roles: Iterable[str],
    presets: Dict[str, Dict[str, Any]] | None = None,
) -> ComponentRegistry:
    registry = ComponentRegistry()
    mapping = presets or DEFAULT_ATOMS
    for role in sorted(set(roles)):
        atom = mapping.get(role)
        if not atom:
            raise KeyError(f"No preset mapping for role {role!r}")
        spec = ComponentSpec(
            role=role,
            module=atom["module"],
            export=atom.get("export", "default"),
            defaults=atom.get("defaults", {}),
        )
        registry.register(spec)
    return registry


def render(
    site: SiteD,
    route: str,
    *,
    width: int = 1280,
    height: int = 800,
    presets: Dict[str, Dict[str, Any]] | None = None,
) -> str:
    page = next(p for p in site.pages if p.route == route)
    roles: list[str] = []
    specs_by_id: Dict[str, Any] = {}
    d_rows = []

    for row in page.table.rows:
        d_cols = []
        for col in row.cols:
            token = SizeToken(col.size)
            d_blocks = []
            for widget in col.items:
                roles.append(widget.role)
                specs_by_id.setdefault(
                    widget.id,
                    _tile_spec(id=widget.id, role=widget.role, min_w=160, min_h=120),
                )
                d_blocks.append(d_block(widget.id))
            d_cols.append(d_col(*d_blocks, size=token))
        d_rows.append(d_row(*d_cols, height_rows=row.height_rows))

    tbl = d_table(*d_rows, gap_x=page.table.gap_x, gap_y=page.table.gap_y)
    viewport = Viewport(width, height)

    compiler = LayoutCompiler()
    grid_spec, placements, frames_map = compiler.frames_from_structure(tbl, viewport)
    registry = _build_registry(roles, presets=presets)
    view_model = compiler.view_model(
        grid_spec,
        viewport,
        frames_map,
        list(specs_by_id.values()),
        components_registry=registry,
    )
    manifest = build_manifest(view_model)
    return HtmlShell().render(manifest)
