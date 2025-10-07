from __future__ import annotations
from typing import Mapping, Any
from .spec import Manifest
from .utils import (
    build_manifest,
    manifest_to_json as _manifest_to_json,
    manifest_from_json as _manifest_from_json,
)


class ManifestBuilder:
    """Default manifest builder; thin class wrapper over utils.build_manifest()."""

    def build(
        self, view_model: Mapping[str, Any], *, version: str = "2025.10"
    ) -> Manifest:
        return build_manifest(view_model, version=version)

    # --- context manager support ---
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


def manifest_to_json(manifest: Manifest, *, indent: int | None = None) -> str:
    return _manifest_to_json(manifest, indent=indent)


def manifest_from_json(data: str | Mapping[str, Any]) -> Manifest:
    return _manifest_from_json(data)
