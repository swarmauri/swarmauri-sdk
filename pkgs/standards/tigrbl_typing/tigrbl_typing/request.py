from __future__ import annotations

from dataclasses import dataclass
from typing import Any


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
        return f"{path}?{query_string}" if query_string else path


@dataclass(frozen=True)
class AwaitableValue:
    value: Any

    def __await__(self):
        async def _value() -> Any:
            return self.value

        return _value().__await__()


__all__ = ["URL", "AwaitableValue"]
