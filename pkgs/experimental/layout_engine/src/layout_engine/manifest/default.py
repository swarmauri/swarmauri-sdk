from __future__ import annotations

from typing import Any, Mapping

from collections.abc import Iterable
from typing import Sequence

from ..site.spec import SiteSpec
from ..events.validators import register_channels as _register_channels
from .spec import ChannelManifest, Manifest, WsRouteManifest
from .utils import (
    build_manifest,
    manifest_to_json as _manifest_to_json,
    manifest_from_json as _manifest_from_json,
)


def _site_to_payload(
    site: SiteSpec | None, active_page: str | None = None
) -> dict | None:
    if site is None:
        return None
    pages = [
        {
            "id": page.id,
            "route": page.route,
            "title": page.title,
            "slots": [slot.model_dump() for slot in page.slots],
            "meta": dict(page.meta),
        }
        for page in site.pages
    ]
    return {
        "pages": pages,
        "active_page": active_page,
        "navigation": {"base_path": site.base_path},
    }


def _channels_to_payload(
    channels: Sequence[ChannelManifest] | Iterable[ChannelManifest] | None,
) -> list[dict] | None:
    if not channels:
        return None
    payload: list[dict] = []
    for entry in channels:
        if isinstance(entry, ChannelManifest):
            payload.append(entry.model_dump())
        else:
            payload.append(ChannelManifest.model_validate(entry).model_dump())
    return payload


def _routes_to_payload(
    routes: Sequence[WsRouteManifest] | Iterable[WsRouteManifest] | None,
) -> list[dict] | None:
    if not routes:
        return None
    payload: list[dict] = []
    for entry in routes:
        if isinstance(entry, WsRouteManifest):
            payload.append(entry.model_dump())
        else:
            payload.append(WsRouteManifest.model_validate(entry).model_dump())
    return payload


class ManifestBuilder:
    """Default manifest builder with optional site metadata injection."""

    def build(
        self,
        view_model: Mapping[str, Any],
        *,
        version: str = "2025.10",
        site: SiteSpec | None = None,
        active_page: str | None = None,
        channels: Sequence[ChannelManifest] | Iterable[ChannelManifest] | None = None,
        ws_routes: Sequence[WsRouteManifest] | Iterable[WsRouteManifest] | None = None,
    ) -> Manifest:
        if site is not None and "site" not in view_model:
            site_payload = _site_to_payload(site, active_page=active_page)
            if site_payload is not None:
                view_model = dict(view_model)
                view_model["site"] = site_payload
        if channels and "channels" not in view_model:
            channel_payload = _channels_to_payload(channels)
            if channel_payload:
                view_model = dict(view_model)
                view_model["channels"] = channel_payload
        if ws_routes and "ws_routes" not in view_model:
            route_payload = _routes_to_payload(ws_routes)
            if route_payload:
                view_model = dict(view_model)
                view_model["ws_routes"] = route_payload
        manifest = build_manifest(view_model, version=version)
        if manifest.channels:
            _register_channels([ch.model_dump() for ch in manifest.channels])
        return manifest

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
