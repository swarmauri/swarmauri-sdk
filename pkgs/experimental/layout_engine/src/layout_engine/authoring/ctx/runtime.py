from __future__ import annotations
import json
from typing import Dict, Any, Iterable
from wsgiref.simple_server import make_server

from ...core.size import SizeToken
from ...tiles import tile_spec as _tile_spec
from ... import (
    # structure/compile/manifest
    block as d_block,
    col as d_col,
    row as d_row,
    table as d_table,
    LayoutCompiler,
    Viewport,
    build_manifest,
    # components + targets
    ComponentRegistry,
    define_component,
    HtmlShell,
    HtmlExporter,
    SvgExporter,
    PdfExporter,
    CodeExporter,
)
from ..widgets import _Base as _WidgetBase
from ...contrib.presets import DEFAULT_ATOMS
from .builder import TableCtx


def _to_token(size: str) -> SizeToken:
    try:
        return SizeToken(size)
    except Exception:
        raise ValueError(f"Invalid column size token: {size!r}")


def _build_registry(
    roles: Iterable[str], *, presets: Dict[str, Dict[str, Any]] | None = None
) -> ComponentRegistry:
    reg = ComponentRegistry()
    mapping = presets or DEFAULT_ATOMS
    for role in sorted(set(roles)):
        atom = mapping.get(role)
        if not atom:
            raise KeyError(f"No preset mapping for role {role!r}")
        define_component(
            reg,
            role=role,
            module=atom["module"],
            export=atom["export"],
            defaults=atom["defaults"],
        )
    return reg


def compile_table(
    table: TableCtx,
    *,
    width: int = 1280,
    height: int = 800,
    presets: Dict[str, Dict[str, Any]] | None = None,
):
    roles = []
    specs_by_id: Dict[str, Any] = {}
    d_rows = []
    for r in table.rows:
        d_cols = []
        for c in r.cols:
            token = _to_token(c.size)
            d_blocks = []
            for w in c.items:
                if not isinstance(w, _WidgetBase):
                    raise TypeError(f"Unsupported item in column: {w!r}")
                roles.append(w.role)
                specs_by_id.setdefault(
                    w.id, _tile_spec(id=w.id, role=w.role, min_w=160, min_h=120)
                )
                d_blocks.append(d_block(w.id))
            d_cols.append(d_col(*d_blocks, size=token))
        d_rows.append(d_row(*d_cols, height_rows=r.height_rows))
    tbl = d_table(*d_rows, gap_x=table.gap_x, gap_y=table.gap_y)

    vp = Viewport(width, height)
    compiler = LayoutCompiler()
    gs, placements, frames = compiler.frames_from_structure(tbl, vp)
    reg = _build_registry(roles, presets=presets)
    vm = compiler.view_model(
        gs, vp, frames, list(specs_by_id.values()), components_registry=reg
    )
    return build_manifest(vm)


def render_table(
    table: TableCtx,
    *,
    width: int = 1280,
    height: int = 800,
    presets: Dict[str, Dict[str, Any]] | None = None,
) -> str:
    m = compile_table(table, width=width, height=height, presets=presets)
    return HtmlShell().render(m)


def export_table(
    table: TableCtx,
    *,
    out: str,
    format: str = "html",
    width: int = 1280,
    height: int = 800,
    presets: Dict[str, Dict[str, Any]] | None = None,
) -> str:
    m = compile_table(table, width=width, height=height, presets=presets)
    match format:
        case "html":
            return HtmlExporter().export(m, out=out)
        case "svg":
            return SvgExporter().export(m, out=out)
        case "pdf":
            return PdfExporter().export(m, out=out)
        case "code":
            return CodeExporter().export(m, out=out)
        case _:
            raise ValueError("unsupported format")


def serve_table(
    table: TableCtx,
    *,
    host: str = "127.0.0.1",
    port: int = 8789,
    width: int = 1280,
    height: int = 800,
    presets: Dict[str, Dict[str, Any]] | None = None,
):
    m = compile_table(table, width=width, height=height, presets=presets)
    html = HtmlShell().render(m)

    def app(environ, start_response):
        path = environ.get("PATH_INFO", "/")
        if path == "/":
            start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
            return [html.encode("utf-8")]
        if path == "/manifest.json":
            start_response("200 OK", [("Content-Type", "application/json")])
            return [
                json.dumps(m.to_dict(), separators=(",", ":"), sort_keys=True).encode(
                    "utf-8"
                )
            ]
        start_response("404 Not Found", [("Content-Type", "text/plain")])
        return [b"not found"]

    print(f"Serving table at http://{host}:{port}/")
    make_server(host, port, app).serve_forever()
