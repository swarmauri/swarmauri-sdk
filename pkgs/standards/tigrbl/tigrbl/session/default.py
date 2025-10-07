from __future__ import annotations

import inspect
from typing import Any, Callable, Optional

from .base import TigrblSessionBase
from .spec import SessionSpec


class DefaultSession(TigrblSessionBase):
    """
    Delegating session that wraps an underlying native session object
    (sync or async) and exposes the Tigrbl Session ABC.

    No third-party imports: we rely on duck-typed methods on the underlying
    object (begin/commit/rollback, add/delete/flush/refresh/get/execute/close).
    """

    def __init__(self, underlying: Any, spec: Optional[SessionSpec] = None) -> None:
        super().__init__(spec)
        self._u = underlying

    # ---- async marker ----
    async def run_sync(self, fn: Callable[[Any], Any]) -> Any:
        rv = fn(self._u)
        if inspect.isawaitable(rv):
            return await rv
        return rv

    # ---- TX primitives ----
    async def _tx_begin_impl(self) -> None:
        fn = getattr(self._u, "begin", None)
        if not callable(fn):
            raise RuntimeError("underlying session does not support begin()")
        rv = fn()
        if inspect.isawaitable(rv):
            await rv

    async def _tx_commit_impl(self) -> None:
        fn = getattr(self._u, "commit", None)
        if not callable(fn):
            raise RuntimeError("underlying session does not support commit()")
        rv = fn()
        if inspect.isawaitable(rv):
            await rv

    async def _tx_rollback_impl(self) -> None:
        fn = getattr(self._u, "rollback", None)
        if not callable(fn):
            raise RuntimeError("underlying session does not support rollback()")
        rv = fn()
        if inspect.isawaitable(rv):
            await rv

    def in_transaction(self) -> bool:
        it = getattr(self._u, "in_transaction", None)
        if callable(it):
            try:
                return bool(it())
            except Exception:
                pass
        return super().in_transaction()

    # ---- CRUD primitives ----
    def _add_impl(self, obj: Any) -> Any:
        fn = getattr(self._u, "add", None)
        if not callable(fn):
            raise NotImplementedError("underlying session does not implement add(obj)")
        return fn(obj)

    async def _delete_impl(self, obj: Any) -> None:
        fn = getattr(self._u, "delete", None)
        if not callable(fn):
            raise NotImplementedError(
                "underlying session does not implement delete(obj)"
            )
        rv = fn(obj)
        if inspect.isawaitable(rv):
            await rv

    async def _flush_impl(self) -> None:
        fn = getattr(self._u, "flush", None)
        if callable(fn):
            rv = fn()
            if inspect.isawaitable(rv):
                await rv

    async def _refresh_impl(self, obj: Any) -> None:
        fn = getattr(self._u, "refresh", None)
        if callable(fn):
            rv = fn(obj)
            if inspect.isawaitable(rv):
                await rv

    async def _get_impl(self, model: type, ident: Any) -> Any | None:
        fn = getattr(self._u, "get", None)
        if not callable(fn):
            raise NotImplementedError(
                "underlying session does not implement get(model, ident)"
            )
        rv = fn(model, ident)
        return await rv if inspect.isawaitable(rv) else rv

    async def _execute_impl(self, stmt: Any) -> Any:
        fn = getattr(self._u, "execute", None)
        if not callable(fn):
            raise NotImplementedError(
                "underlying session does not implement execute(stmt)"
            )
        rv = fn(stmt)
        return await rv if inspect.isawaitable(rv) else rv

    async def _close_impl(self) -> None:
        fn = getattr(self._u, "close", None)
        if callable(fn):
            rv = fn()
            if inspect.isawaitable(rv):
                await rv
