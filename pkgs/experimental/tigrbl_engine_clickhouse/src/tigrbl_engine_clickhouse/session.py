from __future__ import annotations
from typing import Any, Optional

from tigrbl.session.base import TigrblSessionBase  # first-class session base


class ClickHouseSession(TigrblSessionBase):
    """A Tigrbl session backed by clickhouse-connect (sync client).

    This concrete session implements the async hooks expected by
    :class:`TigrblSessionBase`. ClickHouse does not provide general-purpose
    transactions; the tx hooks are treated as no-ops.
    """

    def __init__(self, engine: Any, *, url: Optional[str] = None) -> None:
        super().__init__()
        self._engine = engine
        self._url_override = url
        self._client = None

    # ---- client lifecycle -------------------------------------------------
    @property
    def client(self):
        if self._client is None:
            try:
                import clickhouse_connect
            except Exception as e:  # pragma: no cover
                raise RuntimeError(
                    "clickhouse-connect is required for ClickHouseSession"
                ) from e

            if self._url_override or self._engine.url:
                # clickhouse-connect supports URL form
                self._client = clickhouse_connect.get_client(
                    url=self._url_override or self._engine.url
                )
            else:
                self._client = clickhouse_connect.get_client(
                    host=self._engine.host,
                    port=self._engine.port,
                    username=self._engine.username,
                    password=self._engine.password,
                    database=self._engine.database,
                    secure=self._engine.secure,
                    verify=self._engine.verify,
                    **self._engine.kwargs,
                )
        return self._client

    # ---- TigrblSessionBase hooks -----------------------------------------
    async def _tx_begin_impl(self) -> None:  # no-op; ClickHouse has limited tx support
        return None

    async def _tx_commit_impl(self) -> None:
        return None

    async def _tx_rollback_impl(self) -> None:
        return None

    def _add_impl(self, obj: Any) -> Any:
        raise NotImplementedError(
            "ClickHouseSession.add is not supported; use _execute_impl with INSERT"
        )

    async def _delete_impl(self, obj: Any) -> None:
        raise NotImplementedError(
            "ClickHouseSession.delete is not supported; use _execute_impl with DELETE"
        )

    async def _flush_impl(self) -> None:
        # No buffering by default
        return None

    async def _refresh_impl(self, obj: Any) -> None:
        return None

    async def _get_impl(self, model: type, ident: Any) -> Any | None:
        # Generic ORM-style get is not applicable; return None
        return None

    async def _execute_impl(self, stmt: Any) -> Any:
        """Execute a SQL statement.

        - If `stmt` is a string, route SELECT-like statements to `query()`,
          others to `command()`.
        - If `stmt` is a callable, call it with the underlying client.
        """
        if callable(stmt):
            return stmt(self.client)

        if not isinstance(stmt, str):
            raise NotImplementedError(
                f"Unsupported stmt type: {type(stmt)}; expected SQL string or callable"
            )

        sql = stmt.strip()
        # Heuristic: treat SELECT/SHOW/DESCRIBE/EXPLAIN as queries
        prefix = sql.split(None, 1)[0].upper() if sql else ""
        if prefix in {"SELECT", "WITH", "SHOW", "DESCRIBE", "EXPLAIN"}:
            res = self.client.query(sql)
            # Return rows (list of tuples). Caller can access names via res.column_names
            try:
                return res.result_rows  # clickhouse-connect 0.6+
            except Exception:
                return getattr(res, "rows", res)
        else:
            return self.client.command(sql)

    async def _close_impl(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            finally:
                self._client = None
