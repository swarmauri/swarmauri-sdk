from __future__ import annotations
from ...manifest.spec import Manifest
from ..base import IWebGuiTarget


class HtmlShell(IWebGuiTarget):
    """Render a minimal SSR HTML snippet for a single page manifest.

    This does not emit <html>/<head>; it returns a <div class='page'> block intended to be
    embedded into a larger shell (e.g., SiteRouter.render_shell).
    """

    def render(self, manifest: Manifest, *, out: str | None = None) -> str:
        tiles_html = []
        for t in manifest.tiles:
            f = t.frame
            style = f"position:absolute;left:{int(f['x'])}px;top:{int(f['y'])}px;width:{int(f['w'])}px;height:{int(f['h'])}px;"
            tiles_html.append(
                f"<div class='tile' data-tile='{t.id}' style='{style}'></div>"
            )
        page_style = "position:relative;min-height:100vh;"
        return (
            "<div class='page' style='"
            + page_style
            + "'>"
            + "".join(tiles_html)
            + "</div>"
        )
