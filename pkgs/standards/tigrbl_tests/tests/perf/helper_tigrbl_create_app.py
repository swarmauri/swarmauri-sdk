from __future__ import annotations

import inspect
import sqlite3
from pathlib import Path

from tigrbl import TableBase, TigrblApp
from tigrbl.shortcuts.engine import sqlitef
from tigrbl.types import Column, Integer, String


def _build_benchmark_item_model() -> type[TableBase]:
    class TigrblBenchmarkItem(TableBase):
        __tablename__ = "benchmark_tigrbl_item"
        __allow_unmapped__ = True

        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String, nullable=False)

    return TigrblBenchmarkItem


def create_tigrbl_app(db_path: Path) -> TigrblApp:
    """Build a Tigrbl app with a single create command endpoint."""
    app = TigrblApp(engine=sqlitef(str(db_path), async_=False))
    app.include_table(_build_benchmark_item_model())
    app.attach_diagnostics(prefix="", app=app)
    return app


async def initialize_tigrbl_app(app: TigrblApp) -> None:
    init_result = app.initialize()
    if inspect.isawaitable(init_result):
        await init_result


def fetch_tigrbl_names(db_path: Path) -> list[str]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT name FROM benchmark_tigrbl_item ORDER BY rowid"
        ).fetchall()
    return [row[0] for row in rows]


def tigrbl_create_path() -> str:
    return "/tigrblbenchmarkitem"
