from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import numpy as np
import pandas as pd

from tigrbl_engine_pandas.engine import DataFrameCatalog

from .session import NumpySession


@dataclass
class NumpyEngine:
    """Single-table NumPy engine: one array/matrix behaves like one table database."""

    array: np.ndarray
    table: str
    pk: str
    catalog: DataFrameCatalog


def numpy_engine(
    *, mapping: dict[str, Any] | None = None, **_: Any
) -> tuple[NumpyEngine, Callable[[], NumpySession]]:
    """Build the ``numpy`` engine handle and session factory for tigrbl."""
    config = dict(mapping or {})
    raw_array = config.get("array")
    if raw_array is None:
        raise TypeError("mapping['array'] is required")

    table = config.get("table", "records")
    pk = config.get("pk", "id")
    columns = config.get("columns")

    if not isinstance(table, str) or not table:
        raise TypeError("mapping['table'] must be a non-empty string")
    if not isinstance(pk, str) or not pk:
        raise TypeError("mapping['pk'] must be a non-empty string")

    array = raw_array if isinstance(raw_array, np.ndarray) else np.asarray(raw_array)
    frame = pd.DataFrame(array, columns=columns)
    catalog = DataFrameCatalog(tables={table: frame}, pks={table: pk})
    engine = NumpyEngine(array=array, table=table, pk=pk, catalog=catalog)

    def session_factory() -> NumpySession:
        return NumpySession(engine)

    return engine, session_factory


def numpy_capabilities() -> dict[str, object]:
    return {
        "ndarray": True,
        "single_table_database": True,
        "dataframe": True,
        "transactions": True,
        "dialect": "numpy",
    }
