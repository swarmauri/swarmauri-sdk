from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Dict, Any, Iterable

from ..authoring.widgets import _Base as _WidgetBase
from ..contrib.presets import DEFAULT_ATOMS
from ..core.size import SizeToken
from ..tiles import tile_spec as _tile_spec
from .. import (
    block as d_block, col as d_col, row as d_row, table as d_table,
    LayoutCompiler, Viewport, build_manifest,
    ComponentRegistry, define_component, HtmlShell
)

@dataclass(frozen=True)  class ColD:  size: str; items: Tuple[_WidgetBase, ...]
@dataclass(frozen=True)  class RowD:  height_rows: int; cols: Tuple[ColD, ...]
@dataclass(frozen=True)  class TableD: rows: Tuple[RowD, ...]; gap_x: int = 12; gap_y: int = 12
@dataclass(frozen=True)  class PageD:  route: str; title: str; table: TableD
@dataclass(frozen=True)  class SiteD:  base_path: str = "/"; pages: Tuple[PageD, ...] = ()

def _build_registry(roles: Iterable[str], presets: Dict[str, Dict[str, Any]] | None = None) -> ComponentRegistry:
    from .. import define_component, ComponentRegistry
    reg = ComponentRegistry()
    mapping = presets or DEFAULT_ATOMS
    for role in sorted(set(roles)):
        atom = mapping.get(role)
        if not atom:
            raise KeyError(f"No preset mapping for role {role!r}")
        define_component(reg, role=role, module=atom["module"], export=atom["export"], defaults=atom["defaults"])
    return reg

def render(site: SiteD, route: str, *, width: int = 1280, height: int = 800, presets: Dict[str, Dict[str, Any]] | None = None) -> str:
    page = next(p for p in site.pages if p.route == route)
    roles = []; specs_by_id: Dict[str, Any] = {}; d_rows = []
    for r in page.table.rows:
        d_cols = []
        for c in r.cols:
            token = SizeToken(c.size); d_blocks = []
            for w in c.items:
                roles.append(w.role)
                specs_by_id.setdefault(w.id, _tile_spec(id=w.id, role=w.role, min_w=160, min_h=120))
                d_blocks.append(d_block(w.id))
            d_cols.append(d_col(*d_blocks, size=token))
        d_rows.append(d_row(*d_cols, height_rows=r.height_rows))
    tbl = d_table(*d_rows, gap_x=page.table.gap_x, gap_y=page.table.gap_y)
    vp = Viewport(width, height)
    comp = LayoutCompiler()
    gs, placements, frames = comp.frames_from_structure(tbl, vp)
    reg = _build_registry(roles, presets=presets)
    vm = comp.view_model(gs, vp, frames, list(specs_by_id.values()), components_registry=reg)
    return HtmlShell().render(build_manifest(vm))
