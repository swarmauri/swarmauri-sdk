from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import threading
from typing import Any, Callable

import numpy as np

from .session import NumpySession


@dataclass
class NumpyCatalog:
    rows: list[dict[str, Any]] = field(default_factory=list)
    columns: list[str] = field(default_factory=list)
    pk: str = "id"
    table_ver: int = 0
    lock: threading.RLock = field(default_factory=threading.RLock)

    def bump(self) -> None:
        self.table_ver += 1


@dataclass
class NumpyEngine:
    """Single-table NumPy engine: one ndarray/memmap behaves like one table DB."""

    array: np.ndarray
    table: str
    pk: str
    columns: list[str]
    catalog: NumpyCatalog


def _rows_from_array(array: np.ndarray, columns: list[str]) -> list[dict[str, Any]]:
    if array.ndim == 0:
        matrix = np.asarray([[array.item()]], dtype=object)
    elif array.ndim == 1:
        matrix = np.asarray(array, dtype=object).reshape(-1, 1)
    else:
        matrix = np.asarray(array, dtype=object)
    return [dict(zip(columns, row, strict=False)) for row in matrix.tolist()]


def _resolve_array(config: dict[str, Any]) -> np.ndarray:
    if (raw_array := config.get("array")) is not None:
        return raw_array if isinstance(raw_array, np.ndarray) else np.asarray(raw_array)

    if (
        path_value := config.get("path")
        or config.get("load_path")
        or config.get("file")
    ):
        path = Path(path_value)
        loaded = np.load(path, mmap_mode=config.get("mmap_mode"))
        if isinstance(loaded, np.lib.npyio.NpzFile):
            npz_key = config.get("npz_key")
            if npz_key is None:
                if len(loaded.files) != 1:
                    raise ValueError(
                        "mapping['npz_key'] is required for multi-array .npz files"
                    )
                npz_key = loaded.files[0]
            return np.asarray(loaded[npz_key])
        return np.asarray(loaded)

    if (memmap_path := config.get("memmap_path")) is not None:
        mode = config.get("memmap_mode", "r+")
        valid_modes = {"r", "r+", "w+", "c"}
        if mode not in valid_modes:
            raise ValueError(
                f"mapping['memmap_mode'] must be one of {sorted(valid_modes)}"
            )
        dtype = config.get("dtype", np.float64)
        shape = config.get("shape")
        if mode == "w+" and shape is None:
            raise ValueError("mapping['shape'] is required when memmap_mode='w+'")
        return np.memmap(memmap_path, dtype=dtype, mode=mode, shape=shape)

    raise TypeError(
        "Provide one of mapping['array'], mapping['path']/['load_path']/['file'], or mapping['memmap_path']"
    )


def numpy_engine(
    *, mapping: dict[str, Any] | None = None, **_: Any
) -> tuple[NumpyEngine, Callable[[], NumpySession]]:
    """Build the ``numpy`` engine handle and session factory for tigrbl."""
    config = dict(mapping or {})
    table = config.get("table", "records")
    pk = config.get("pk", "id")
    if not isinstance(table, str) or not table:
        raise TypeError("mapping['table'] must be a non-empty string")
    if not isinstance(pk, str) or not pk:
        raise TypeError("mapping['pk'] must be a non-empty string")

    array = _resolve_array(config)
    inferred_cols = 1 if array.ndim <= 1 else int(array.shape[1])
    columns = list(
        config.get("columns") or [f"col_{idx}" for idx in range(inferred_cols)]
    )
    if pk not in columns:
        columns = [pk, *columns]

    rows = _rows_from_array(array, columns)
    catalog = NumpyCatalog(rows=rows, columns=columns, pk=pk)
    engine = NumpyEngine(
        array=array, table=table, pk=pk, columns=columns, catalog=catalog
    )

    def session_factory() -> NumpySession:
        return NumpySession(engine)

    return engine, session_factory


def numpy_capabilities() -> dict[str, object]:
    return {
        "ndarray": True,
        "single_table_database": True,
        "file_formats": ["npy", "npz"],
        "memmap_modes": ["r", "r+", "w+", "c"],
        "transactions": True,
        "dialect": "numpy",
    }
