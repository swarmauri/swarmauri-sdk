from __future__ import annotations

from typing import Any


class BloomSession:
    def __init__(self, engine: Any) -> None:
        self._engine = engine
        self._closed = False

    def close(self) -> None:
        self._closed = True

    def add(self, key: bytes | str) -> None:
        self._require_open()
        self._engine.add(key)

    def contains(self, key: bytes | str) -> bool:
        self._require_open()
        return self._engine.contains(key)

    def __contains__(self, key: bytes | str) -> bool:
        return self.contains(key)

    def add_if_absent(self, key: bytes | str) -> bool:
        self._require_open()
        return self._engine.add_if_absent(key)

    def reset(self) -> None:
        self._require_open()
        self._engine.reset()

    def stats(self) -> dict:
        self._require_open()
        return self._engine.stats()

    def _require_open(self) -> None:
        if self._closed:
            raise RuntimeError("session is closed")


class AsyncBloomSession(BloomSession):
    async def close(self) -> None:  # type: ignore[override]
        super().close()
