from __future__ import annotations
from typing import Mapping, Any
from .spec import Manifest
from .utils import build_manifest

class ManifestBuilder:
    """Default manifest builder; thin class wrapper over utils.build_manifest()."""
    def build(self, view_model: Mapping[str, Any], *, version: str = "2025.10") -> Manifest:
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
