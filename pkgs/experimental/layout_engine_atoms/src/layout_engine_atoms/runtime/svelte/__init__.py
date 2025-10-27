"""Thin Svelte runtime adapter for layout-engine manifests.

This module mirrors the Vue server integration but serves the Svelte client
bundle instead of the Vue assets.
"""

from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import Any, Mapping

from ..vue import (
    ManifestBuilder,
    ManifestEventsConfig,
    ManifestWebSocket,
    ManifestApp as _VueManifestApp,
)


def load_client_assets(root: Path | None = None) -> dict[str, bytes]:
    """Return packaged client assets for the Svelte runtime."""

    client_root = Path(__file__).resolve().parent / "client"
    core_root = client_root.parent.parent / "core"
    sources: list[Path] = []
    if root is not None:
        sources.append(root)
    else:
        dist_root = client_root / "dist"
        if dist_root.exists():
            sources.append(dist_root)
        sources.append(client_root)

    assets: dict[str, bytes] = {}
    for base in sources:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file():
                relative_key = path.relative_to(base).as_posix()
                assets.setdefault(relative_key, path.read_bytes())

    if core_root.exists():
        for path in core_root.rglob("*.js"):
            if path.is_file():
                relative_key = Path("core") / path.relative_to(core_root)
                assets.setdefault(relative_key.as_posix(), path.read_bytes())

    return assets


class ManifestApp(_VueManifestApp):
    """Serve manifests and static assets for the Svelte runtime."""

    def __init__(self, *args: Any, catalog: str = "svelte", **kwargs: Any) -> None:
        super().__init__(*args, catalog=catalog, **kwargs)

    @cached_property
    def assets(self) -> Mapping[str, bytes]:  # type: ignore[override]
        if self.static_assets is not None:
            return self.static_assets
        return load_client_assets()


def create_layout_app(
    *,
    manifest_builder: ManifestBuilder,
    mount_path: str = "/",
    **options: Any,
) -> ManifestApp:
    """Create a ManifestApp pre-configured with Svelte assets."""

    return ManifestApp(
        manifest_builder=manifest_builder,
        mount_path=mount_path,
        **options,
    )


__all__ = [
    "ManifestApp",
    "ManifestBuilder",
    "ManifestEventsConfig",
    "ManifestWebSocket",
    "create_layout_app",
    "load_client_assets",
]
