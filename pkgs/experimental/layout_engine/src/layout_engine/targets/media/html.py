from __future__ import annotations
from pathlib import Path
from typing import Iterable, Mapping, Any
from ..base import IMediaTarget
from ...manifest.spec import Manifest

_MIN_CSS = """html,body{margin:0;padding:0}
.page{position:relative;min-height:100vh}
.tile{position:absolute;box-sizing:border-box}
"""


class HtmlExporter(IMediaTarget):
    """
    Styled HTML exporter with optional CSS links and inline CSS.
    - Maintains class name and interface: export(manifest, out=...)->str
    - Adds styling controls via constructor, but defaults are backward compatible.
    """

    def __init__(
        self,
        *,
        title: str | None = None,
        css_links: Iterable[str] | None = None,
        inline_css: str | None = None,
        include_min_css: bool = True,
        lang: str = "en",
        dir: str = "ltr",
        extra_head: str | None = None,
        body_attrs: Mapping[str, Any] | None = None,
    ) -> None:
        self.title = title or "Layout"
        self.css_links = list(css_links or [])
        self.inline_css = inline_css or ""
        self.include_min_css = include_min_css
        self.lang = lang
        self.dir = dir
        self.extra_head = extra_head or ""
        self.body_attrs = dict(body_attrs or {})

    def export(self, manifest: Manifest, *, out: str) -> str:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        vw = int(manifest.viewport.get("width", 1280))
        vh = int(manifest.viewport.get("height", 800))

        head_parts: list[str] = [
            "<meta charset='utf-8'>",
            "<meta name='viewport' content='width=device-width, initial-scale=1'>",
            f"<title>{self.title}</title>",
        ]
        for href in self.css_links:
            head_parts.append(f"<link rel='stylesheet' href='{href}'>")

        css_chunks = []
        if self.include_min_css:
            css_chunks.append(_MIN_CSS)
        if self.inline_css:
            css_chunks.append(self.inline_css)

        if css_chunks:
            head_parts.append("<style>" + "".join(css_chunks) + "</style>")

        if self.extra_head:
            head_parts.append(self.extra_head)

        body_attr_parts: list[str] = []
        for key, value in self.body_attrs.items():
            safe_value = str(value).replace("'", "&#39;")
            body_attr_parts.append(f"{key}='{safe_value}'")
        body_attr_str = " ".join(body_attr_parts)

        # Tiles
        tiles_html = []
        for t in manifest.tiles:
            if isinstance(t, Mapping):
                frame_data = t.get("frame", {})
                tid = t.get("id", "")
            else:
                frame_obj = getattr(t, "frame", {})
                frame_data = (
                    frame_obj.to_dict()
                    if hasattr(frame_obj, "to_dict")
                    else dict(frame_obj)
                )
                tid = getattr(t, "id", "")
            x = int(frame_data.get("x", 0))
            y = int(frame_data.get("y", 0))
            w = int(frame_data.get("w", 0))
            h = int(frame_data.get("h", 0))
            # Allow a subtle default border to make areas visible; leave style hook for external CSS.
            style = f"left:{x}px;top:{y}px;width:{w}px;height:{h}px;"
            tiles_html.append(
                f"<div class='tile' data-tile='{tid}' style='{style}'></div>"
            )

        html = (
            "<!doctype html>"
            f"<html lang='{self.lang}' dir='{self.dir}'>"
            "<head>" + "".join(head_parts) + "</head>"
            f"<body {body_attr_str}>"
            f"<div class='page' style='width:{vw}px;height:{vh}px'>"
            + "".join(tiles_html)
            + "</div></body></html>"
        )
        Path(out).write_text(html, encoding="utf-8")
        return str(out)
