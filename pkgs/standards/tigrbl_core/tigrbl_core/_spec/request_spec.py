from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional

from .serde import SerdeMixin


@dataclass(slots=True)
class RequestSpec(SerdeMixin):
    method: str = "GET"
    path: str = "/"
    headers: Mapping[str, str] = field(default_factory=dict)
    query: Dict[str, List[str]] = field(default_factory=dict)
    path_params: Dict[str, str] = field(default_factory=dict)
    body: bytes = b""
    script_name: str = ""
    app: Optional[Any] = None


__all__ = ["RequestSpec"]
