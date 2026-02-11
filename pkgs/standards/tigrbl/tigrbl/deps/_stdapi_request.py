"""Request model for stdapi router compatibility."""

from __future__ import annotations

import json as json_module
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any


@dataclass
class Request:
    method: str
    path: str
    headers: dict[str, str]
    query: dict[str, list[str]]
    path_params: dict[str, str]
    body: bytes
    script_name: str = ""
    app: Any | None = None
    state: SimpleNamespace = field(default_factory=SimpleNamespace)
    scope: dict[str, Any] = field(default_factory=dict)

    def json(self) -> Any:
        if not self.body:
            return None
        return json_module.loads(self.body.decode("utf-8"))

    def query_param(self, name: str, default: str | None = None) -> str | None:
        vals = self.query.get(name)
        if not vals:
            return default
        return vals[0]

    @property
    def url(self) -> str:
        base = (self.script_name or "").rstrip("/")
        query_string = "&".join(
            f"{name}={value}" for name, values in self.query.items() for value in values
        )
        path = f"{base}{self.path}" if base else self.path
        if query_string:
            return f"{path}?{query_string}"
        return path

    @property
    def query_params(self) -> dict[str, str]:
        return {name: vals[0] for name, vals in self.query.items() if vals}
