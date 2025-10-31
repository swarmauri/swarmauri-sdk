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
    dist_root = client_root / "dist"

    candidate_sources: list[Path] = []
    if root is not None:
        candidate_sources.append(root)
    elif dist_root.exists():
        candidate_sources.append(dist_root)
    else:
        candidate_sources.append(client_root)

    assets: dict[str, bytes] = {}

    dist_root_resolved = dist_root.resolve()

    def _should_include(path: Path, base: Path) -> bool:
        if base.resolve() == dist_root_resolved:
            return True
        relative = path.relative_to(base)
        if "node_modules" in relative.parts:
            return False
        return relative.suffix in {".js", ".mjs", ".cjs", ".css", ".html", ".json"}

    for base in candidate_sources:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file():
                if not _should_include(path, base):
                    continue
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

    def _asset_response(  # type: ignore[override]
        self, asset_path: str
    ) -> tuple[int, list[tuple[str, str]], bytes]:
        status, headers, body = super()._asset_response(asset_path)
        if status != 200 or not body:
            return status, headers, body

        try:
            html = body.decode("utf-8")
        except UnicodeDecodeError:
            return status, headers, body

        if asset_path and asset_path != self.index_asset:
            return status, headers, body

        styles: list[str] = []
        for key, blob in self.assets.items():
            if not key.lower().endswith(".css"):
                continue
            try:
                styles.append(blob.decode("utf-8"))
            except UnicodeDecodeError:
                continue

        if not styles:
            return status, headers, body

        style_tag = "<style>\n" + "\n\n".join(styles) + "\n</style>"
        if "</head>" in html:
            html = html.replace("</head>", f"  {style_tag}\n</head>", 1)
        else:
            html = f"{style_tag}\n" + html

        updated_body = html.encode("utf-8")
        headers = [(k, v) for k, v in headers if k.lower() != "content-length"]
        headers.append(("content-length", str(len(updated_body))))
        return status, headers, updated_body


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
