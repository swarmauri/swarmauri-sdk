from __future__ import annotations

import json as json_module
from dataclasses import dataclass, field
from http.cookies import SimpleCookie
from types import SimpleNamespace
from typing import Any
from collections.abc import Iterable, Mapping
from urllib.parse import parse_qs

from tigrbl_core._spec.request_spec import RequestSpec


from tigrbl_typing.request import AwaitableValue, URL


@dataclass(init=False)
class Request(RequestSpec):
    method: str
    path: str
    headers: Mapping[str, str] | Iterable[tuple[str, str]]
    query: dict[str, list[str]]
    path_params: dict[str, str]
    body: bytes
    script_name: str = ""
    app: Any | None = None
    state: SimpleNamespace = field(default_factory=SimpleNamespace)
    scope: dict[str, Any] = field(default_factory=dict)
    _json_cache: Any = field(default=None, init=False, repr=False)
    _json_loaded: bool = field(default=False, init=False, repr=False)

    def __init__(
        self,
        method: str | dict[str, Any],
        path: str | None = None,
        headers: Mapping[str, str] | Iterable[tuple[str, str]] | None = None,
        query: dict[str, list[str]] | None = None,
        path_params: dict[str, str] | None = None,
        body: bytes = b"",
        script_name: str = "",
        app: Any | None = None,
        state: SimpleNamespace | None = None,
        scope: dict[str, Any] | None = None,
        receive: Any | None = None,
    ) -> None:
        del receive

        self._json_cache = None
        self._json_loaded = False

        if isinstance(method, dict):
            if scope is not None:
                raise TypeError("scope cannot be provided when first argument is scope")
            self._init_from_scope(method, app=app, state=state)
            return

        if path is None:
            raise TypeError("path is required when constructing Request from fields")

        self.method = method
        self.path = path
        self.headers = headers or {}
        self.query = query or {}
        self.path_params = path_params or {}
        self.body = body
        self.script_name = script_name
        self.app = app
        self.state = state or SimpleNamespace()
        self.scope = scope or {}

    def _init_from_scope(
        self,
        scope: dict[str, Any],
        *,
        app: Any | None,
        state: SimpleNamespace | None,
    ) -> None:
        self.method = (scope.get("method") or "GET").upper()
        self.path = scope.get("path") or "/"
        self.headers = {
            key.decode("latin-1").lower(): value.decode("latin-1")
            for key, value in scope.get("headers", [])
        }
        self.query = parse_qs(
            scope.get("query_string", b"").decode("latin-1"), keep_blank_values=True
        )
        self.path_params = scope.get("path_params") or {}
        self.body = b""
        self.script_name = scope.get("root_path") or ""
        self.app = app
        self.state = state or SimpleNamespace()
        self.scope = scope

    @classmethod
    def from_scope(
        cls,
        scope: dict[str, Any],
        receive: Any | None = None,
        *,
        app: Any | None = None,
        state: SimpleNamespace | None = None,
    ) -> "Request":
        return cls(scope, app=app, state=state, receive=receive)

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

    @property
    def bearer_token(self) -> str | None:
        authorization = self.headers.get("authorization", "") or ""
        scheme, _, token = authorization.partition(" ")
        cleaned = token.strip()
        return cleaned if scheme.lower() == "bearer" and cleaned else None

    @property
    def admin_key(self) -> str | None:
        key = (self.headers.get("x-admin-key") or "").strip()
        return key or None

    @property
    def session_token(self) -> str | None:
        return self.bearer_token or (self.cookies.get("sid") or "").strip() or None

    @property
    def client(self) -> SimpleNamespace:
        host = ""
        client = self.scope.get("client") if isinstance(self.scope, dict) else None
        if isinstance(client, tuple) and client:
            host = str(client[0])
        return SimpleNamespace(ip=host, host=host)


__all__ = ["Request", "URL", "AwaitableValue"]
