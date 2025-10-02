from __future__ import annotations
from typing import Protocol, Any
from ..manifest.spec import Manifest

class ITarget(Protocol):
    """Abstract rendering/export target."""
    def render(self, manifest: Manifest, *, out: str | None = None) -> Any: ...

class IWebGuiTarget(ITarget, Protocol):
    """Web GUI page shells (SSR HTML) for hosts to hydrate."""
    def render(self, manifest: Manifest, *, out: str | None = None) -> str: ...

class IMediaTarget(ITarget, Protocol):
    """Offline artifact exporters (PDF/SVG/HTML/Code)."""
    def export(self, manifest: Manifest, *, out: str) -> str: ...
