# File: peagen/manifest_writer.py
from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
import typer

class ManifestWriter:
    """
    Streams JSON-Lines during file generation, then composes a final
    <slug>_manifest.json matching Peagen’s schema.

    ── Life-cycle ─────────────────────────────────────────────────────
    • add(...)      → append one line and background-upload the partial
    • finalise()    → build the full JSON manifest, upload, clean up
    """

    # ──────────────────────────────────────────────────────── init ──
    def __init__(
        self,
        *,
        slug: str,
        adapter,
        tmp_root: Path,
        meta: Dict[str, Any] | None = None,
    ) -> None:
        """
        Parameters
        ----------
        slug         Project slug (e.g. ``"ExampleParserProject"``).
        adapter      Storage adapter implementing ``upload(key, file)``.
        tmp_root     Workspace/.peagen directory (created if absent).
        meta         Static fields for the final manifest (schema_version,
                     workspace_uri, project, source_packages, peagen_version…)
        """
        tmp_root.mkdir(parents=True, exist_ok=True)

        self.slug = slug
        self.adapter = adapter
        self.meta: Dict[str, Any] = meta or {}

        #  <slug>_manifest.partial.jsonl   (streamed while building)
        self.path = tmp_root / f"{slug}_manifest.partial.jsonl"
        self._lock = threading.Lock()

    # ─────────────────────────────────────────────────────── add ──
    def add(self, entry: Dict[str, Any]) -> None:
        """
        Thread-safe append *entry* to *.partial.jsonl* and upload it so
        external tools can tail the manifest in near-realtime.
        """
        with self._lock:
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, separators=(",", ":")) + "\n")

        # async, best-effort upload of the partial
        threading.Thread(
            target=self._upload_partial,
            name=f"upload-{self.slug}",
            daemon=True,
        ).start()

    # ────────────────────────────────────────────────── finalise ──
    def finalise(self) -> Path:
        """
        •  Read *.partial.jsonl*  → list of generated file paths
        •  Compose final manifest dict  (+ generated_at timestamp)
        •  Write <slug>_manifest.json, upload, and clean intermediates
        •  Return local path to the finished manifest
        """
        # Destination …/ExampleParserProject_manifest.json
        final_path = self.path.with_name(
            self.path.name.replace("_manifest.partial", "_manifest")
        ).with_suffix(".json")

        # build `generated` list
        with self.path.open("r", encoding="utf-8") as src:
            generated_files = [json.loads(line)["file"] for line in src]

        manifest: Dict[str, Any] = dict(self.meta)
        manifest["generated"] = generated_files
        manifest["generated_at"] = datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        )

        with final_path.open("w", encoding="utf-8") as dst:
            json.dump(manifest, dst, indent=2)

        # upload finished manifest
        with final_path.open("rb") as fh:
            self.adapter.upload(f".peagen/{final_path.name}", fh)

        # tidy up partial artefacts
        self.path.unlink(missing_ok=True)


        typer.echo(f"\n📄 manifest → {self.adapter.root_uri}.peagen/{final_path.name}")

        return final_path

    # ───────────────────────────────────────────── helper ──
    def _upload_partial(self) -> None:
        """Fire-and-forget upload of the current *.partial.jsonl* file."""
        try:
            with self.path.open("rb") as fh:
                self.adapter.upload(f".peagen/{self.path.name}", fh)
        except Exception:  # pragma: no cover
            pass
