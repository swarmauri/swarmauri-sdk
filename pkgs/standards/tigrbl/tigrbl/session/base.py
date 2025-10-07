from __future__ import annotations

import asyncio
import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional

from .abc import SessionABC
from .spec import SessionSpec


@dataclass
class TigrblSessionBase(SessionABC):
    """
    Common session behavior:
      - Tracks SessionSpec
      - Tracks transaction state (_open) and write intent (_dirty)
      - Queues accidentally-async add() work and resolves on flush/commit
      - Enforces read-only both on write calls and at commit
    """

    _spec: Optional[SessionSpec] = None

    _open: bool = field(default=False, init=False)
    _dirty: bool = field(default=False, init=False)
    _pending: List[asyncio.Task] = field(default_factory=list, init=False)

    # ---- utilities ----
    def apply_spec(self, spec: SessionSpec | None) -> None:
        self._spec = spec

    async def run_sync(self, fn: Callable[[Any], Any]) -> Any:
        """
        Default async marker: run the callback against *this* session.
        Subclasses may override to pass the native handle.
        """
        rv = fn(self)
        if inspect.isawaitable(rv):
            return await rv
        return rv

    # ---- TX template methods ----
    async def begin(self) -> None:
        await self._tx_begin_impl()
        self._open = True

    async def commit(self) -> None:
        # late guard
        if self._spec and self._spec.read_only and self._dirty:
            raise RuntimeError("read-only session: writes detected before commit")
        await self.flush()
        await self._tx_commit_impl()
        self._open = False
        self._dirty = False

    async def rollback(self) -> None:
        # cancel queued add() tasks
        for t in self._pending:
            try:
                t.cancel()
            except Exception:
                pass
        self._pending.clear()
        await self._tx_rollback_impl()
        self._open = False
        self._dirty = False

    def in_transaction(self) -> bool:
        return bool(self._open)

    # ---- CRUD surface (template) ----
    def add(self, obj: Any) -> None:
        if self._spec and self._spec.read_only:
            raise RuntimeError("write attempted in read-only session (add)")
        self._dirty = True
        rv = self._add_impl(obj)
        if inspect.isawaitable(rv):
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                asyncio.run(rv)
            else:
                self._pending.append(loop.create_task(rv))

    async def delete(self, obj: Any) -> None:
        if self._spec and self._spec.read_only:
            raise RuntimeError("write attempted in read-only session (delete)")
        self._dirty = True
        await self._delete_impl(obj)

    async def flush(self) -> None:
        if self._pending:
            done, _ = await asyncio.wait(
                self._pending, return_when=asyncio.ALL_COMPLETED
            )
            self._pending = []
            # surface any exception
            for t in done:
                _ = t.result()
        await self._flush_impl()

    async def refresh(self, obj: Any) -> None:
        await self._refresh_impl(obj)

    async def get(self, model: type, ident: Any) -> Any | None:
        return await self._get_impl(model, ident)

    async def execute(self, stmt: Any) -> Any:
        return await self._execute_impl(stmt)

    async def close(self) -> None:
        for t in self._pending:
            try:
                t.cancel()
            except Exception:
                pass
        self._pending = []
        await self._close_impl()

    # ---- abstract primitives ----
    async def _tx_begin_impl(self) -> None:  # pragma: no cover - abstract hook
        raise NotImplementedError

    async def _tx_commit_impl(self) -> None:  # pragma: no cover - abstract hook
        raise NotImplementedError

    async def _tx_rollback_impl(self) -> None:  # pragma: no cover - abstract hook
        raise NotImplementedError

    def _add_impl(self, obj: Any) -> Any:  # pragma: no cover - abstract hook
        raise NotImplementedError

    async def _delete_impl(self, obj: Any) -> None:  # pragma: no cover - abstract hook
        raise NotImplementedError

    async def _flush_impl(self) -> None:  # pragma: no cover - abstract hook
        return

    async def _refresh_impl(self, obj: Any) -> None:  # pragma: no cover - abstract hook
        return

    async def _get_impl(
        self, model: type, ident: Any
    ) -> Any | None:  # pragma: no cover
        raise NotImplementedError

    async def _execute_impl(self, stmt: Any) -> Any:  # pragma: no cover - abstract hook
        raise NotImplementedError

    async def _close_impl(self) -> None:  # pragma: no cover - abstract hook
        return
