from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import pandas as pd

from tigrbl_engine_pandas.engine import DataFrameCatalog

from .session import CsvSession


@dataclass
class CsvEngine:
    """Single-table CSV engine: one CSV file behaves like one table database."""

    path: str
    table: str
    pk: str
    catalog: DataFrameCatalog


def csv_engine(
    *, mapping: dict[str, Any] | None = None, **_: Any
) -> tuple[CsvEngine, Callable[[], CsvSession]]:
    """Build the ``csv`` engine handle and session factory for tigrbl."""
    config = dict(mapping or {})
    path = config.get("path") or config.get("file")
    if not isinstance(path, str) or not path:
        raise TypeError("mapping['path'] (or 'file') must be a non-empty string")

    table = config.get("table", "records")
    pk = config.get("pk", "id")
    read_csv_options = config.get("read_csv_options", {})

    if not isinstance(table, str) or not table:
        raise TypeError("mapping['table'] must be a non-empty string")
    if not isinstance(pk, str) or not pk:
        raise TypeError("mapping['pk'] must be a non-empty string")
    if not isinstance(read_csv_options, dict):
        raise TypeError("mapping['read_csv_options'] must be dict[str, Any]")

    frame = pd.read_csv(path, **read_csv_options)
    catalog = DataFrameCatalog(tables={table: frame}, pks={table: pk})
    engine = CsvEngine(path=path, table=table, pk=pk, catalog=catalog)

    def session_factory() -> CsvSession:
        return CsvSession(engine)

    return engine, session_factory


def csv_capabilities() -> dict[str, object]:
    return {
        "files": ["csv"],
        "single_table_database": True,
        "dataframe": True,
        "transactions": True,
        "dialect": "csv",
    }
