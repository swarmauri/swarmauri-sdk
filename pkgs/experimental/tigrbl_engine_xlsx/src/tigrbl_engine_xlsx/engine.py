from __future__ import annotations

from dataclasses import dataclass, field
import threading
from typing import Any, Callable, Dict

import pandas as pd

from .session import XlsxSession


@dataclass
class WorkbookCatalog:
    tables: Dict[str, pd.DataFrame] = field(default_factory=dict)
    pks: Dict[str, str] = field(default_factory=dict)
    table_ver: Dict[str, int] = field(default_factory=dict)
    lock: threading.RLock = field(default_factory=threading.RLock)

    def get_live(self, name: str) -> pd.DataFrame:
        if name not in self.tables:
            self.tables[name] = pd.DataFrame()
            self.table_ver[name] = 0
        self.table_ver.setdefault(name, 0)
        return self.tables[name]

    def bump(self, name: str) -> None:
        self.table_ver[name] = self.table_ver.get(name, 0) + 1


@dataclass
class XlsxEngine:
    """Workbook-backed engine: workbook as DB, sheet names as table names."""

    path: str
    pk: str
    catalog: WorkbookCatalog


def xlsx_engine(
    *, mapping: dict[str, Any] | None = None, **_: Any
) -> tuple[XlsxEngine, Callable[[], XlsxSession]]:
    config = dict(mapping or {})
    path = config.get("path") or config.get("file")
    if not isinstance(path, str) or not path:
        raise TypeError("mapping['path'] (or 'file') must be a non-empty string")

    pk = config.get("pk", "id")
    if not isinstance(pk, str) or not pk:
        raise TypeError("mapping['pk'] must be a non-empty string")

    frames = pd.read_excel(path, sheet_name=None)
    if not isinstance(frames, dict) or not frames:
        raise ValueError("workbook must contain at least one sheet")

    catalog = WorkbookCatalog(
        tables={str(sheet): frame for sheet, frame in frames.items()},
        pks={str(sheet): pk for sheet in frames},
    )
    engine = XlsxEngine(path=path, pk=pk, catalog=catalog)

    def session_factory() -> XlsxSession:
        return XlsxSession(engine)

    return engine, session_factory


def xlsx_capabilities() -> dict[str, object]:
    return {
        "files": ["xlsx"],
        "workbook_database": True,
        "multi_table": True,
        "dataframe": True,
        "transactions": True,
        "dialect": "xlsx",
    }
