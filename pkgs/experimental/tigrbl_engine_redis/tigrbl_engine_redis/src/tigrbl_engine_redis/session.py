from __future__ import annotations

import inspect
from typing import Any, Callable, Optional

from tigrbl.session.base import TigrblSessionBase  # first-class session base

class RedisSession(TigrblSessionBase):
    """A Tigrbl session backed by a Redis client (async).

    This is a concrete subclass of Tigrbl's first-class session base. It wraps
    a `redis.asyncio.Redis` client, exposing a minimal set of primitives to
    satisfy the Session ABC. It treats Redis commands as statements for
    `_execute_impl` and offers simple key/value helpers for `_get_impl`.
    """
    def __init__(self, engine: Any, *, url: Optional[str] = None) -> None:
        super().__init__()
        self._engine = engine
        self._url_override = url
        self._client = None
        self._pipe = None

    # ---- client lifecycle -------------------------------------------------
    @property
    def client(self):
        if self._client is None:
            try:
                from redis.asyncio import Redis
            except Exception as e:  # pragma: no cover
                raise RuntimeError("redis>=5.0.0 is required for RedisSession") from e
            if self._url_override or self._engine.url:
                self._client = Redis.from_url(self._url_override or self._engine.url)  # type: ignore[arg-type]
            else:
                self._client = Redis(host=self._engine.host, port=self._engine.port, db=self._engine.db)
        return self._client

    def _target(self):
        """Return active pipeline if in a tx, else the client."""
        return self._pipe if self._pipe is not None else self.client

    # ---- TigrblSessionBase hooks -----------------------------------------
    async def _tx_begin_impl(self) -> None:
        self._pipe = self.client.pipeline(transaction=True)

    async def _tx_commit_impl(self) -> None:
        if self._pipe is not None:
            await self._pipe.execute()
        self._pipe = None

    async def _tx_rollback_impl(self) -> None:
        if self._pipe is not None:
            # pipeline.reset() discards queued commands
            reset = getattr(self._pipe, "reset", None)
            if callable(reset):
                rv = reset()
                if inspect.isawaitable(rv):
                    await rv
        self._pipe = None

    def _add_impl(self, obj: Any) -> Any:
        """Best-effort 'add' for key/value; accepts {'key': k, 'value': v} or (k, v)."""
        if isinstance(obj, dict) and "key" in obj and "value" in obj:
            return self._target().set(obj["key"], obj["value"])
        if isinstance(obj, (list, tuple)) and len(obj) == 2:
            k, v = obj
            return self._target().set(k, v)
        raise NotImplementedError("RedisSession.add expects {'key','value'} or (key, value)")

    async def _delete_impl(self, obj: Any) -> None:
        key = obj if isinstance(obj, str) else getattr(obj, "key", None)
        if not key:
            raise NotImplementedError("RedisSession.delete expects a key (str)")
        await self._target().delete(key)

    async def _flush_impl(self) -> None:
        # No-op for Redis; commands are sent immediately or on execute()
        return

    async def _refresh_impl(self, obj: Any) -> None:
        # No-op for key/value
        return

    async def _get_impl(self, model: type, ident: Any) -> Any | None:
        # Interpret ident as a key; model is ignored in this simple adapter
        return await self._target().get(ident)

    async def _execute_impl(self, stmt: Any) -> Any:
        """Execute a Redis command.
        - If `stmt` is a callable, call it with the underlying client/pipe.
        - If `stmt` is a tuple/list like ('SET','k','v'), look up the method.
        - If `stmt` is a raw command string, use execute_command().
        """
        tgt = self._target()
        if callable(stmt):
            rv = stmt(tgt)
            return await rv if inspect.isawaitable(rv) else rv
        if isinstance(stmt, (list, tuple)) and stmt:
            cmd, *args = stmt
            fn = getattr(tgt, str(cmd).lower(), None)
            if not callable(fn):
                # Fall back to execute_command
                return await tgt.execute_command(str(cmd), *args)
            rv = fn(*args)
            return await rv if inspect.isawaitable(rv) else rv
        if isinstance(stmt, str):
            return await tgt.execute_command(stmt)
        raise NotImplementedError(f"Unsupported stmt type: {type(stmt)}")

    async def _close_impl(self) -> None:
        if self._pipe is not None:
            try:
                reset = getattr(self._pipe, "reset", None)
                if callable(reset):
                    rv = reset()
                    if inspect.isawaitable(rv):
                        await rv
            finally:
                self._pipe = None
        if self._client is not None:
            close = getattr(self._client, "close", None)
            if callable(close):
                rv = close()
                if inspect.isawaitable(rv):
                    await rv
            self._client = None

    # ---- async marker override -------------------------------------------
    async def run_sync(self, fn: Callable[[Any], Any]) -> Any:
        """Run a callback against the *underlying Redis client or pipeline*."""
        rv = fn(self._target())
        return await rv if inspect.isawaitable(rv) else rv
