from __future__ import annotations
import pickle
from typing import Any, Optional

from redis import Redis
from sqlalchemy.orm import Session as SASession
from tigrbl.session import TigrblSessionBase, SessionSpec

class CacheThroughSession(TigrblSessionBase):
    """A Tigrbl session that wraps a SQLAlchemy Session plus a Redis client.

    Implements simple read-through caching for `get(model, ident)` and
    write-through invalidation on delete/commit. For demonstration purposes;
    tune keys/ttl/serialization to your domain.
    """

    def __init__(
        self,
        sa_session: SASession,
        redis_client: Redis,
        cache_ttl_sec: int = 60,
        key_prefix: str = "tigrbl:ct",
        spec: Optional[SessionSpec] = None,
    ) -> None:
        super().__init__(spec)
        self._sa = sa_session
        self._r = redis_client
        self._ttl = int(cache_ttl_sec)
        self._prefix = key_prefix

    # ---- transaction primitives ----
    async def _tx_begin_impl(self) -> None:
        self._sa.begin()

    async def _tx_commit_impl(self) -> None:
        self._sa.commit()

    async def _tx_rollback_impl(self) -> None:
        self._sa.rollback()

    # ---- CRUD primitives ----
    def _cache_key(self, model: type, ident: Any) -> str:
        return f"{self._prefix}:{model.__module__}.{getattr(model, '__name__', str(model))}:{ident}"

    def _add_impl(self, obj: Any) -> Any:
        # Delegate to SA; cache writes happen on commit/refresh if desired.
        return self._sa.add(obj)

    async def _delete_impl(self, obj: Any) -> None:
        # Best-effort invalidation if PK is available
        pk = getattr(obj, 'id', None)
        if pk is not None:
            key = self._cache_key(type(obj), pk)
            try:
                self._r.delete(key)
            except Exception:
                pass
        self._sa.delete(obj)

    async def _flush_impl(self) -> None:
        self._sa.flush()

    async def _refresh_impl(self, obj: Any) -> None:
        self._sa.refresh(obj)

    async def _get_impl(self, model: type, ident: Any) -> Any | None:
        key = self._cache_key(model, ident)
        try:
            blob = self._r.get(key)
        except Exception:
            blob = None
        if blob:
            try:
                return pickle.loads(blob)
            except Exception:
                # Corrupted cache entry; drop it and fall through
                try:
                    self._r.delete(key)
                except Exception:
                    pass

        # Cache miss → DB
        obj = self._sa.get(model, ident)
        if obj is not None:
            try:
                self._r.setex(key, self._ttl, pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL))
            except Exception:
                # Cache is best-effort
                pass
        return obj

    async def _execute_impl(self, stmt: Any) -> Any:
        # No caching by default; delegate to DB
        return self._sa.execute(stmt)

    async def _close_impl(self) -> None:
        try:
            self._sa.close()
        finally:
            try:
                # Redis >= 4
                close = getattr(self._r, 'close', None)
                if callable(close):
                    close()
            except Exception:
                pass
