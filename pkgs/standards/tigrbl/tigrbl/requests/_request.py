"""Transport-level HTTP request model used by stdapi adapters."""

from __future__ import annotations

import base64
import json as json_module
from dataclasses import dataclass, field
from http.cookies import SimpleCookie
from types import SimpleNamespace
from typing import Any
from collections.abc import Iterable, Mapping
from urllib.parse import parse_qs

from tigrbl.headers import HeaderCookies, Headers


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

    def __getattr__(self, name: str) -> Any:
        attr = getattr(self.value, name)
        if callable(attr):

            def _wrapped(*args: Any, **kwargs: Any) -> Any:
                return attr(*args, **kwargs)

            return _wrapped
        return attr

    def __iter__(self):
        return iter(self.value)

    def __len__(self) -> int:
        return len(self.value)


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64url_decode(data: str) -> bytes:
    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + pad).encode("ascii"))


@dataclass(init=False)
class Request:
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
        """Create a request from canonical fields or an ASGI scope.

        The compatibility path accepts ``Request(scope, receive=...)`` to ease
        migrations from frameworks whose request objects support that calling
        convention. The ``receive`` callable is accepted for API compatibility
        but not consumed directly by this transport model.
        """

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
        self.__post_init__()

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
            scope.get("query_string", b"").decode("latin-1"),
            keep_blank_values=True,
        )
        self.path_params = scope.get("path_params") or {}
        self.body = b""
        self.script_name = scope.get("root_path") or ""
        self.app = app
        self.state = state or SimpleNamespace()
        self.scope = scope
        self.__post_init__()

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
    def cookies(self) -> HeaderCookies:
        raw = self.headers.get("cookie", "") or ""
        parsed = SimpleCookie()
        parsed.load(raw)
        return HeaderCookies({name: morsel.value for name, morsel in parsed.items()})

    @property
    def bearer_token(self) -> str | None:
        authorization = self.headers.get("authorization", "") or ""
        scheme, _, token = authorization.partition(" ")
        cleaned = token.strip()
        if scheme.lower() == "bearer" and cleaned:
            return cleaned
        return None

    @property
    def admin_key(self) -> str | None:
        key = (self.headers.get("x-admin-key") or "").strip()
        if key:
            return key
        return None

    @property
    def session_token(self) -> str | None:
        bearer = self.bearer_token
        if bearer:
            return bearer
        cookie_token = (self.cookies.get("sid") or "").strip()
        if cookie_token:
            return cookie_token
        return None

    @property
    def client(self) -> SimpleNamespace:
        host = ""
        try:
            client = self.scope.get("client")
        except AttributeError:
            client = None
        if isinstance(client, tuple) and client:
            host = str(client[0])
        return SimpleNamespace(ip=host, host=host)

    @staticmethod
    def b64url_encode(data: bytes) -> str:
        return _b64url_encode(data)

    @staticmethod
    def b64url_decode(data: str) -> bytes:
        return _b64url_decode(data)


__all__ = ["Request", "AwaitableValue", "URL", "_b64url_encode", "_b64url_decode"]
