from __future__ import annotations
from abc import ABC, abstractmethod, Any
from ..manifest.spec import Manifest

class ITarget(ABC):
    """Abstract rendering/export target."""
    @abstractmethod
    def render(self, manifest: Manifest, *, out: str | None = None) -> Any:
        raise NotImplementedError

class IWebGuiTarget(ITarget, ABC):
    """Web GUI page shells (SSR HTML) for hosts to hydrate."""
    @abstractmethod
    def render(self, manifest: Manifest, *, out: str | None = None) -> str:
        raise NotImplementedError

class IMediaTarget(ITarget, ABC):
    """Offline artifact exporters (PDF/SVG/HTML/Code)."""
    @abstractmethod
    def export(self, manifest: Manifest, *, out: str) -> str:
        raise NotImplementedError
