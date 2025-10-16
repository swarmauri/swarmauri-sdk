"""ASGI entrypoint that serves the Vue dashboard example via ManifestApp."""

from __future__ import annotations

from layout_engine_atoms.examples.vue.generate_manifest import create_manifest
from layout_engine_atoms.runtime.vue import ManifestApp

app = ManifestApp(
    manifest_builder=create_manifest,
    mount_path="/dashboard",
).asgi_app()

__all__ = ["app"]
