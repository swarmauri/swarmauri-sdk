from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional


@dataclass(slots=True)
class RequestSpec:
    method: str = "GET"
    path: str = "/"
    headers: Mapping[str, str] = field(default_factory=dict)
    query: Dict[str, List[str]] = field(default_factory=dict)
    path_params: Dict[str, str] = field(default_factory=dict)
    body: bytes = b""
    script_name: str = ""
    app: Optional[Any] = None


__all__ = ["RequestSpec"]
