"""Shared case-insensitive HTTP header mapping primitives."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, MutableMapping
from typing import Any
from http.cookies import SimpleCookie


class HeaderCookies(dict[str, str]):
    """Dot-addressable cookie mapping parsed from a Cookie header value."""

    def __getattr__(self, name: str) -> str:
        try:
            return self[name]
        except KeyError as exc:  # pragma: no cover - defensive
            raise AttributeError(name) from exc


class SetCookieHeader(str):
    """String-like Set-Cookie header value with cookie-name lookup convenience."""

    def get(self, name: str, default: str | None = None) -> str | None:
        parsed = SimpleCookie()
        parsed.load(str(self))
        morsel = parsed.get(name)
        if morsel is None:
            return default
        return morsel.value


class Headers(MutableMapping[str, str]):
    """Case-insensitive header mapping for request/response objects."""

    def __init__(
        self,
        values: Iterable[tuple[str, str]] | Mapping[str, str] | None = None,
    ) -> None:
        self._data: dict[str, tuple[str, str]] = {}
        if values is None:
            return
        items = values.items() if hasattr(values, "items") else values
        for key, value in items:
            self[key] = self._normalize_value(value)

    @staticmethod
    def _normalize_key(key: Any) -> str:
        if isinstance(key, (bytes, bytearray)):
            return key.decode("latin-1").lower()
        return str(key).lower()

    @staticmethod
    def _normalize_value(value: Any) -> str:
        if isinstance(value, (bytes, bytearray)):
            return value.decode("latin-1")
        return str(value)

    @staticmethod
    def _attribute_key(name: str) -> str:
        return name.replace("_", "-").lower()

    @staticmethod
    def _parse_cookie_header(value: str) -> HeaderCookies:
        parsed = SimpleCookie()
        parsed.load(value)
        return HeaderCookies({name: morsel.value for name, morsel in parsed.items()})

    @staticmethod
    def _coerce_lookup_value(key: str, value: str) -> str | SetCookieHeader:
        if key == "set-cookie":
            return SetCookieHeader(value)
        return value

    def __getitem__(self, key: str) -> str | SetCookieHeader:
        normalized = self._normalize_key(key)
        return self._coerce_lookup_value(normalized, self._data[normalized][1])

    def __setitem__(self, key: str, value: str) -> None:
        lower = self._normalize_key(key)
        normalized_value = self._normalize_value(value)
        if lower == "set-cookie" and lower in self._data:
            existing = self._data[lower][1]
            merged = f"{existing}, {normalized_value}" if existing else normalized_value
            self._data[lower] = (lower, merged)
            return
        self._data[lower] = (lower, normalized_value)

    def __delitem__(self, key: str) -> None:
        del self._data[self._normalize_key(key)]

    def __iter__(self):
        for original, _ in self._data.values():
            yield original

    def __len__(self) -> int:
        return len(self._data)

    def items(self):
        return ((k, v) for k, v in self._data.values())

    def as_list(self) -> list[tuple[str, str]]:
        return list(self.items())

    def append(self, item: tuple[str, str]) -> None:
        key, value = item
        self[key] = value

    def __contains__(self, item: object) -> bool:
        if isinstance(item, tuple) and len(item) == 2:
            key, value = item
            if not isinstance(key, str):
                return False
            current = self.get(key)
            return current == str(value) if current is not None else False
        if isinstance(item, str):
            return self.get(item) is not None
        return False

    def get(self, key: str, default: str | None = None) -> str | SetCookieHeader | None:
        normalized = self._normalize_key(key)
        item = self._data.get(normalized)
        if item is None:
            return default
        return self._coerce_lookup_value(normalized, item[1])

    def __getattr__(self, name: str) -> str | HeaderCookies:
        key = self._attribute_key(name)
        if key not in self._data:
            raise AttributeError(name)
        value = self._data[key][1]
        if key == "cookie":
            return self._parse_cookie_header(value)
        return value

    def __setattr__(self, name: str, value: str) -> None:
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return
        self[self._attribute_key(name)] = value


__all__ = ["Headers", "HeaderCookies", "SetCookieHeader"]
