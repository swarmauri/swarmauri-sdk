from __future__ import annotations
from pathlib import Path
from ..base import IMediaTarget
from ...manifest.spec import Manifest

class PdfExporter(IMediaTarget):
    def export(self, manifest: Manifest, *, out: str) -> str:
        """Placeholder PDF export.
        Writes a companion HTML next to the desired PDF path to be converted downstream by a renderer.
        """
        html_path = Path(out).with_suffix(".html")
        html = ["<!doctype html><html><head><meta charset='utf-8'><title>PDF placeholder</title></head><body>"]
        html.append(f"<pre>PDF export placeholder for {manifest.kind} etag={manifest.etag}</pre>")
        html.append("</body></html>")
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text("".join(html), encoding="utf-8")
        return str(out)
