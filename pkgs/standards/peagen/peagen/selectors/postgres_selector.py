"""PostgresSelector
==================
Selects the *k* rows with the highest scalar fitness from a PostgreSQL table.

Uses a server-side cursor to avoid loading the entire table into memory.
"""

from __future__ import annotations

from typing import List
import psycopg2

from .base import Selector, ParentRef


class PostgresSelector(Selector):
    """Return the ``k`` parents with the highest fitness from Postgres."""

    name = "postgres"

    def __init__(
        self,
        *,
        dsn: str,
        table: str,
        fitness_col: str,
        sha_col: str,
        k: int = 5,
        extra_where: str | None = None,
    ) -> None:
        self.dsn = dsn
        self.table = table
        self.fitness_col = fitness_col
        self.sha_col = sha_col
        self.k = k
        self.extra_where = extra_where or "TRUE"

    # ------------------------------------------------------------------
    def select(self) -> List[ParentRef]:
        """Return the best parents by descending fitness."""

        query = (
            f"SELECT {self.sha_col}, {self.fitness_col} "
            f"FROM {self.table} "
            f"WHERE {self.extra_where} "
            f"ORDER BY {self.fitness_col} DESC, created_at DESC "
            f"LIMIT {self.k}"
        )
        with psycopg2.connect(self.dsn) as conn, conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
        return [ParentRef(commit_sha=r[0], fitness=float(r[1])) for r in rows]
