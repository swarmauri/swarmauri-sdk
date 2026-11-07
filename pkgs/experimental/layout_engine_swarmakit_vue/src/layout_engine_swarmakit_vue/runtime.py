from __future__ import annotations

import json
from textwrap import dedent
from typing import Dict

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from layout_engine import (
    CodeExporter,
    HtmlExporter,
    HtmlShell,
    LayoutCompiler,
    PdfExporter,
    Viewport,
    build_manifest,
    block as d_block,
    col as d_col,
    row as d_row,
    table as d_table,
)
from layout_engine.authoring.ctx.builder import TableCtx
from layout_engine.authoring.widgets import _Base as _WidgetBase
from layout_engine.core.size import SizeToken
from layout_engine.manifest.spec import Manifest
from layout_engine.tiles import tile_spec as _tile_spec

from .presets import create_swarmakit_registry

SWARMAKIT_CDN_VERSION = "0.0.22"


class _TileShim(dict):
    def __getattr__(self, item: str):
        try:
            return self[item]
        except KeyError as exc:  # pragma: no cover - mirrors dict attr access
            raise AttributeError(item) from exc


class _ManifestShim:
    def __init__(self, manifest: Manifest):
        self.tiles = [_TileShim(tile) for tile in manifest.tiles]


def _to_size_token(size: str) -> SizeToken:
    try:
        return SizeToken(size)
    except Exception as exc:  # pragma: no cover - defensive guard
        raise ValueError(f"Invalid column size token: {size!r}") from exc


def _render_shell(manifest: Manifest) -> str:
    return HtmlShell().render(_ManifestShim(manifest))


def compile_swarmakit_table(
    table: TableCtx,
    *,
    width: int = 1280,
    height: int = 800,
    overrides: Dict[str, Dict[str, object]] | None = None,
) -> Manifest:
    """Compile a ``layout-engine`` table using the Swarmakit Vue presets."""

    roles: list[str] = []
    specs_by_id: dict[str, dict] = {}
    d_rows = []

    for row in table.rows:
        d_cols = []
        for column in row.cols:
            token = _to_size_token(column.size)
            d_blocks = []
            for widget in column.items:
                if not isinstance(widget, _WidgetBase):
                    raise TypeError(f"Unsupported widget type: {type(widget)!r}")
                roles.append(widget.role)
                specs_by_id.setdefault(
                    widget.id,
                    _tile_spec(
                        id=widget.id,
                        role=widget.role,
                        min_w=160,
                        min_h=120,
                        props=dict(widget.props),
                    ),
                )
                d_blocks.append(d_block(widget.id))
            d_cols.append(d_col(*d_blocks, size=token))
        d_rows.append(d_row(*d_cols, height_rows=row.height_rows))

    tbl = d_table(*d_rows, gap_x=table.gap_x, gap_y=table.gap_y)
    viewport = Viewport(width, height)
    compiler = LayoutCompiler()
    grid_spec, _, frames = compiler.frames_from_structure(tbl, viewport)
    registry = create_swarmakit_registry(roles, overrides=overrides)
    view_model = compiler.view_model(
        grid_spec,
        viewport,
        frames,
        list(specs_by_id.values()),
        components_registry=registry,
    )
    return build_manifest(view_model)


def render_swarmakit_table(
    table: TableCtx,
    *,
    width: int = 1280,
    height: int = 800,
    overrides: Dict[str, Dict[str, object]] | None = None,
) -> str:
    """Render the HTML shell for a table with Swarmakit presets applied."""

    manifest = compile_swarmakit_table(
        table, width=width, height=height, overrides=overrides
    )
    return _render_shell(manifest)


def export_swarmakit_table(
    table: TableCtx,
    *,
    out: str,
    format: str = "html",
    width: int = 1280,
    height: int = 800,
    overrides: Dict[str, Dict[str, object]] | None = None,
) -> str:
    """Export a Swarmakit-backed table via the ``layout-engine`` exporters."""

    manifest = compile_swarmakit_table(
        table, width=width, height=height, overrides=overrides
    )
    match format:
        case "html":
            return HtmlExporter().export(manifest, out=out)
        case "svg":
            from layout_engine import (
                SvgExporter,
            )  # local import to avoid unused dependency

            return SvgExporter().export(manifest, out=out)
        case "pdf":
            return PdfExporter().export(manifest, out=out)
        case "code":
            return CodeExporter().export(manifest, out=out)
        case _:
            raise ValueError(f"Unsupported export format: {format}")


def render_swarmakit_page(
    manifest: Manifest,
    *,
    title: str = "Swarmakit Layout",
) -> str:
    """Wrap the ``HtmlShell`` output with a Vue + Swarmakit bootstrapping script."""

    manifest_dict = manifest.model_dump()
    shell = _render_shell(manifest)
    manifest_json = json.dumps(manifest_dict, separators=(",", ":"))
    component_names = sorted(
        {
            tile["component"]["export"]
            for tile in manifest_dict.get("tiles", [])
            if isinstance(tile, dict)
            and isinstance(tile.get("component"), dict)
            and "export" in tile["component"]
        }
    )
    roles = {
        tile["role"]: tile["component"]["export"]
        for tile in manifest_dict.get("tiles", [])
        if isinstance(tile, dict)
        and isinstance(tile.get("component"), dict)
        and "export" in tile["component"]
        and "role" in tile
    }
    imports = ",\n        ".join(component_names)
    role_mapping = ",\n        ".join(
        f"'{role}': {export}" for role, export in sorted(roles.items())
    )
    script = dedent(
        f"""
        <script type="module">
        import {{ createApp, h }} from 'https://cdn.jsdelivr.net/npm/vue@3/dist/vue.esm-browser.js';
        import {{
            {imports}
        }} from 'https://cdn.jsdelivr.net/npm/@swarmakit/vue@{SWARMAKIT_CDN_VERSION}/dist/vue.js';
        import 'https://cdn.jsdelivr.net/npm/@swarmakit/vue@{SWARMAKIT_CDN_VERSION}/dist/style.css';

        const manifest = JSON.parse(document.getElementById('swarmakit-manifest').textContent);
        const components = {{
            {role_mapping}
        }};

        for (const tile of manifest.tiles) {{
            const target = document.querySelector(`[data-tile="${{tile.id}}"]`);
            const component = components[tile.role];
            if (!target || !component) continue;

            const app = createApp({{
                render() {{
                    return h(component, {{ ...tile.props }});
                }},
            }});
            app.mount(target);
        }}
        </script>
        """
    ).strip()

    return dedent(
        f"""
        <!DOCTYPE html>
        <html lang="en">
          <head>
            <meta charset="utf-8" />
            <title>{title}</title>
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <style>
              body {{ font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; }}
              .page {{ background: #0d1117; color: #f0f6fc; padding: 24px; min-height: 100vh; }}
            </style>
          </head>
          <body>
            {shell}
            <script type="application/json" id="swarmakit-manifest">{manifest_json}</script>
            {script}
          </body>
        </html>
        """
    ).strip()


def create_swarmakit_fastapi_app(
    table: TableCtx,
    *,
    title: str = "Swarmakit Layout",
    width: int = 1280,
    height: int = 800,
    overrides: Dict[str, Dict[str, object]] | None = None,
) -> FastAPI:
    """Create a FastAPI application that serves the rendered Swarmakit page."""

    def _compile() -> Manifest:
        return compile_swarmakit_table(
            table, width=width, height=height, overrides=overrides
        )

    app = FastAPI(title=title)

    @app.get("/", response_class=HTMLResponse)
    async def index() -> HTMLResponse:
        manifest = _compile()
        html = render_swarmakit_page(manifest, title=title)
        return HTMLResponse(html)

    @app.get("/manifest.json", response_class=JSONResponse)
    async def manifest_endpoint() -> JSONResponse:
        manifest = _compile()
        return JSONResponse(manifest.model_dump())

    return app


__all__ = [
    "SWARMAKIT_CDN_VERSION",
    "compile_swarmakit_table",
    "create_swarmakit_fastapi_app",
    "export_swarmakit_table",
    "render_swarmakit_page",
    "render_swarmakit_table",
]
