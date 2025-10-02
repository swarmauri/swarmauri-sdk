from __future__ import annotations
from pathlib import Path
from ..base import IMediaTarget
from ...manifest.spec import Manifest

class SvgExporter(IMediaTarget):
    def export(self, manifest: Manifest, *, out: str) -> str:
        vw = int(manifest.viewport.get("width", 1280))
        vh = int(manifest.viewport.get("height", 800))
        parts = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{vw}' height='{vh}' viewBox='0 0 {vw} {vh}'>"]
        parts.append(f"<rect width='{vw}' height='{vh}' fill='white' stroke='none' />")
        for t in manifest.tiles:
            f = t.frame
            x,y,w,h = int(f['x']), int(f['y']), int(f['w']), int(f['h'])
            parts.append(f"<g data-tile='{t.id}' transform='translate({x},{y})'>")
            parts.append(f"<rect width='{w}' height='{h}' fill='none' stroke='#cccccc' />")
            parts.append("</g>")
        parts.append("</svg>")
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text("".join(parts), encoding="utf-8")
        return out
