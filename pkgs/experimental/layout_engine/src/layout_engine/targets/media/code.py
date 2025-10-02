from __future__ import annotations
from pathlib import Path
from ..base import IMediaTarget
from ...manifest.spec import Manifest
import json

class CodeExporter(IMediaTarget):
    def export(self, manifest: Manifest, *, out: str) -> str:
        """Emit a portable page description (JSON) suitable for generating Svelte/Vue/React pages."""
        payload = {
            "kind": manifest.kind,
            "version": manifest.version,
            "viewport": dict(manifest.viewport),
            "grid": dict(manifest.grid),
            "tiles": [t.to_dict() for t in manifest.tiles],
            "etag": manifest.etag,
        }
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return out
