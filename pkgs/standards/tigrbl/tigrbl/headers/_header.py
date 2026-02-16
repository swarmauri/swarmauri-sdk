"""Shared case-insensitive HTTP header mapping primitives."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, MutableMapping
from http.cookies import SimpleCookie


class HeaderCookies(dict[str, str]):
    """Dot-addressable cookie mapping parsed from a Cookie header value."""

    def __getattr__(self, name: str) -> str:
        try:
            return self[name]
        except KeyError as exc:  # pragma: no cover - defensive
            raise AttributeError(name) from exc


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
            lower = key.lower()
            self._data[lower] = (lower, str(value))

    @staticmethod
    def _attribute_key(name: str) -> str:
        return name.replace("_", "-").lower()

    @staticmethod
    def _parse_cookie_header(value: str) -> HeaderCookies:
        parsed = SimpleCookie()
        parsed.load(value)
        return HeaderCookies({name: morsel.value for name, morsel in parsed.items()})

    def __getitem__(self, key: str) -> str:
        return self._data[key.lower()][1]

    def __setitem__(self, key: str, value: str) -> None:
        lower = key.lower()
        self._data[lower] = (lower, str(value))

    def __delitem__(self, key: str) -> None:
        del self._data[key.lower()]

    def __iter__(self):
        for original, _ in self._data.values():
            yield original

    def __len__(self) -> int:
        return len(self._data)

    def items(self):
        return ((k, v) for k, v in self._data.values())

    def as_list(self) -> list[tuple[str, str]]:
        return list(self.items())

    def get(self, key: str, default: str | None = None) -> str | None:
        item = self._data.get(key.lower())
        if item is None:
            return default
        return item[1]

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


__all__ = ["Headers", "HeaderCookies"]
