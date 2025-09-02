from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional

ResponseKind = Literal["auto", "json", "html", "text", "file", "stream", "redirect"]


@dataclass(slots=True)
class TemplateSpec:
    name: str
    search_paths: List[str] = field(default_factory=list)
    package: Optional[str] = None
    auto_reload: Optional[bool] = None
    filters: Dict[str, object] = field(default_factory=dict)
    globals: Dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class ResponseSpec:
    kind: ResponseKind = "auto"
    media_type: Optional[str] = None
    status_code: Optional[int] = None
    headers: Dict[str, str] = field(default_factory=dict)
    envelope: Optional[bool] = None
    template: Optional[TemplateSpec] = None
    filename: Optional[str] = None
    download: Optional[bool] = None
    etag: Optional[str] = None
    cache_control: Optional[str] = None
    redirect_to: Optional[str] = None


@dataclass(slots=True)
class Template(TemplateSpec):
    """Concrete template configuration used at runtime."""


@dataclass(slots=True)
class Response(ResponseSpec):
    """Concrete response configuration used at runtime."""


__all__ = [
    "TemplateSpec",
    "ResponseSpec",
    "ResponseKind",
    "Template",
    "Response",
]
