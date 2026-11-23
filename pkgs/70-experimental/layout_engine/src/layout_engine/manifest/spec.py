from __future__ import annotations

from typing import Any, Mapping, Sequence

from pydantic import BaseModel, Field

from ..events.spec import Scope


class SiteManifest(BaseModel):
    """Optional multi-page context embedded alongside the layout payload."""

    pages: Sequence[Mapping[str, Any]] = Field(default_factory=tuple)
    active_page: str | None = None
    navigation: Mapping[str, Any] = Field(default_factory=dict)


class ChannelManifest(BaseModel):
    """Declarative description of a websocket channel."""

    id: str
    scope: Scope
    topic: str
    description: str | None = None
    payload_schema: Mapping[str, Any] = Field(default_factory=dict)
    meta: Mapping[str, Any] = Field(default_factory=dict)


class WsRouteManifest(BaseModel):
    """Mapping from websocket endpoints to channel identifiers."""

    path: str
    channels: Sequence[str] = Field(default_factory=tuple)
    description: str | None = None
    meta: Mapping[str, Any] = Field(default_factory=dict)


class Manifest(BaseModel):
    """Canonical page manifest with optional multi-page site metadata."""

    kind: str
    version: str
    viewport: Mapping[str, Any]
    grid: Mapping[str, Any]
    tiles: list[Mapping[str, Any]]
    etag: str
    site: SiteManifest | None = None
    channels: Sequence[ChannelManifest] = Field(default_factory=tuple)
    ws_routes: Sequence[WsRouteManifest] = Field(default_factory=tuple)
