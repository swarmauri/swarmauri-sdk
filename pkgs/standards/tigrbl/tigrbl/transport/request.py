"""Transport-level HTTP request model used by stdapi adapters."""

from __future__ import annotations

import json as json_module
from collections.abc import MutableMapping
from http.cookies import SimpleCookie
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any


class Headers(MutableMapping[str, str]):
    """Case-insensitive header mapping."""

    def __init__(self, values: dict[str, str] | None = None) -> None:
        self._data: dict[str, str] = {}
        for key, value in (values or {}).items():
            self._data[key.lower()] = value

    def __getitem__(self, key: str) -> str:
        return self._data[key.lower()]

    def __setitem__(self, key: str, value: str) -> None:
        self._data[key.lower()] = value

    def __delitem__(self, key: str) -> None:
        del self._data[key.lower()]

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def get(self, key: str, default: str | None = None) -> str | None:
        return self._data.get(key.lower(), default)


@dataclass(frozen=True)
class URL:
    path: str
    query: dict[str, list[str]]
    script_name: str = ""

    def __str__(self) -> str:
        base = (self.script_name or "").rstrip("/")
        query_string = "&".join(
            f"{name}={value}" for name, values in self.query.items() for value in values
        )
        path = f"{base}{self.path}" if base else self.path
        if query_string:
            return f"{path}?{query_string}"
        return path


@dataclass(frozen=True)
class AwaitableValue:
    value: Any

    def __await__(self):
        async def _value() -> Any:
            return self.value

        return _value().__await__()

    def __eq__(self, other: object) -> bool:
        return self.value == other

    def __getitem__(self, key: Any) -> Any:
        return self.value[key]

    def __repr__(self) -> str:
        return repr(self.value)


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
    _json_cache: Any = field(default=None, init=False, repr=False)
    _json_loaded: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        self.headers = Headers(self.headers)

    def json(self) -> AwaitableValue:
        return AwaitableValue(self.json_sync())

    def json_sync(self) -> Any:
        if self._json_loaded:
            return self._json_cache
        if not self.body:
            self._json_loaded = True
            self._json_cache = None
            return None
        self._json_cache = json_module.loads(self.body.decode("utf-8"))
        self._json_loaded = True
        return self._json_cache

    def query_param(self, name: str, default: str | None = None) -> str | None:
        vals = self.query.get(name)
        if not vals:
            return default
        return vals[0]

    @property
    def url(self) -> URL:
        return URL(path=self.path, query=self.query, script_name=self.script_name)

    @property
    def query_params(self) -> dict[str, str]:
        return {name: vals[0] for name, vals in self.query.items() if vals}

    @property
    def cookies(self) -> dict[str, str]:
        raw = self.headers.get("cookie", "") or ""
        parsed = SimpleCookie()
        parsed.load(raw)
        return {name: morsel.value for name, morsel in parsed.items()}
