from __future__ import annotations
from pathlib import Path
from ..base import IMediaTarget
from ...manifest.spec import Manifest

_MIN_CSS = """html,body{margin:0} .page{position:relative;min-height:100vh}
.tile{position:absolute;border:1px solid #ddd;border-radius:2px;box-sizing:border-box}
"""

class HtmlExporter(IMediaTarget):
    def export(self, manifest: Manifest, *, out: str) -> str:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        vw = int(manifest.viewport.get("width", 1280))
        vh = int(manifest.viewport.get("height", 800))
        parts = ["<!doctype html><html><head><meta charset='utf-8'>"]
        parts.append(f"<meta name='viewport' content='width=device-width, initial-scale=1'>")
        parts.append(f"<title>export {manifest.version} :: {manifest.etag[:8]}</title>")
        parts.append("<style>" + _MIN_CSS + "</style></head><body>")
        parts.append(f"<div class='page' style='width:{vw}px;height:{vh}px'>")
        for t in manifest.tiles:
            f = t.frame
            style = f"left:{int(f['x'])}px;top:{int(f['y'])}px;width:{int(f['w'])}px;height:{int(f['h'])}px;"
            parts.append(f"<div class='tile' data-tile='{t.id}' style='{style}'></div>")
        parts.append("</div></body></html>")
        Path(out).write_text("".join(parts), encoding="utf-8")
        return out
