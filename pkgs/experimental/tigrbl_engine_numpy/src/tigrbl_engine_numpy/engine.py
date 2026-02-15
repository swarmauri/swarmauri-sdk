from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
import tempfile
import threading
from typing import TYPE_CHECKING, Any, Callable

import numpy as np

if TYPE_CHECKING:
    from .session import NumpySession

_MEMMAP_MODES = {"r", "r+", "w+", "c"}


@dataclass
class NumpyCatalog:
    rows: list[dict[str, Any]] = field(default_factory=list)
    table_ver: int = 0
    lock: threading.RLock = field(default_factory=threading.RLock)

    def bump(self) -> None:
        self.table_ver += 1


def _ensure_supported_suffix(path: str) -> str:
    suffix = Path(path).suffix.lower()
    if suffix not in {".npy", ".npz"}:
        raise ValueError("mapping['path'] must end with .npy or .npz")
    return suffix


def _load_from_path(config: dict[str, Any]) -> tuple[np.ndarray, str | None]:
    path = config.get("path")
    if not isinstance(path, str) or not path:
        raise TypeError("mapping['array'] or mapping['path'] is required")

    if config.get("use_memmap"):
        mode = config.get("mode", "r+")
        if mode not in _MEMMAP_MODES:
            raise ValueError("mapping['mode'] must be one of 'r', 'r+', 'w+', 'c'")
        dtype = config.get("dtype")
        shape = config.get("shape")
        array = np.memmap(path, mode=mode, dtype=dtype, shape=shape)
        persist_path = path if Path(path).suffix.lower() in {".npy", ".npz"} else None
        return np.asarray(array), persist_path

    suffix = _ensure_supported_suffix(path)
    mmap_mode = config.get("mmap_mode")
    if mmap_mode is not None and mmap_mode not in _MEMMAP_MODES:
        raise ValueError("mapping['mmap_mode'] must be one of 'r', 'r+', 'w+', 'c'")

    loaded = np.load(path, allow_pickle=False, mmap_mode=mmap_mode)
    if isinstance(loaded, np.lib.npyio.NpzFile):
        key = config.get("npz_key")
        if key is None:
            files = list(loaded.files)
            if not files:
                raise ValueError("npz file is empty")
            key = files[0]
        return np.asarray(loaded[key]), path

    if suffix == ".npz":
        raise ValueError("npz path must resolve to an array from the archive")

    return np.asarray(loaded), path


def _rows_to_array(rows: list[dict[str, Any]], columns: list[str]) -> np.ndarray:
    data = [[row.get(col) for col in columns] for row in rows]
    return np.asarray(data)


def _array_to_rows(array: np.ndarray, columns: list[str]) -> list[dict[str, Any]]:
    matrix = np.atleast_2d(array)
    return [dict(zip(columns, row.tolist(), strict=False)) for row in matrix]


def atomic_save_array(array: np.ndarray, path: str, *, npz_key: str = "data") -> None:
    suffix = _ensure_supported_suffix(path)
    directory = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".tmp_", suffix=suffix)
    os.close(fd)
    try:
        if suffix == ".npz":
            np.savez(tmp, **{npz_key: array})
        else:
            np.save(tmp, array, allow_pickle=False)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


@dataclass
class NumpyEngine:
    """Single-table NumPy engine: one array/matrix behaves like one table database."""

    array: np.ndarray
    table: str
    pk: str
    columns: list[str]
    catalog: NumpyCatalog
    path: str | None = None
    npz_key: str = "data"


def numpy_engine(
    *, mapping: dict[str, Any] | None = None, **_: Any
) -> tuple[NumpyEngine, Callable[[], NumpySession]]:
    """Build the ``numpy`` engine handle and session factory for tigrbl."""
    config = dict(mapping or {})
    raw_array = config.get("array")
    if raw_array is None:
        array, path = _load_from_path(config)
    else:
        array = (
            raw_array if isinstance(raw_array, np.ndarray) else np.asarray(raw_array)
        )
        path = config.get("path")

    table = config.get("table", "records")
    pk = config.get("pk", "id")
    columns = config.get("columns")
    npz_key = str(config.get("npz_key", "data"))

    if not isinstance(table, str) or not table:
        raise TypeError("mapping['table'] must be a non-empty string")
    if not isinstance(pk, str) or not pk:
        raise TypeError("mapping['pk'] must be a non-empty string")

    if columns is None:
        width = int(np.atleast_2d(array).shape[1]) if array.size else 1
        columns = [pk] + [f"c{i}" for i in range(1, width)]
    columns = [str(col) for col in columns]

    rows = [] if array.size == 0 else _array_to_rows(array, columns)
    catalog = NumpyCatalog(rows=rows)
    engine = NumpyEngine(
        array=_rows_to_array(rows, columns),
        table=table,
        pk=pk,
        columns=columns,
        catalog=catalog,
        path=path,
        npz_key=npz_key,
    )

    from .session import NumpySession

    def session_factory() -> NumpySession:
        return NumpySession(engine)

    return engine, session_factory


def numpy_capabilities() -> dict[str, object]:
    return {
        "ndarray": True,
        "single_table_database": True,
        "file_formats": ["npy", "npz"],
        "memmap_modes": sorted(_MEMMAP_MODES),
        "transactions": True,
        "dialect": "numpy",
    }
