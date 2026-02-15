from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import threading
from typing import Any, Callable

from openpyxl import load_workbook
from openpyxl.workbook import Workbook

from .session import XlsxSession


@dataclass
class WorkbookCatalog:
    workbook: Workbook
    path: str
    tables: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    pks: dict[str, str] = field(default_factory=dict)
    table_ver: dict[str, int] = field(default_factory=dict)
    lock: threading.RLock = field(default_factory=threading.RLock)

    def get_live(self, name: str) -> list[dict[str, Any]]:
        if name not in self.tables:
            self.tables[name] = []
            self.table_ver[name] = 0
            self.pks.setdefault(name, "id")
        self.table_ver.setdefault(name, 0)
        return self.tables[name]

    def bump(self, name: str) -> None:
        self.table_ver[name] = self.table_ver.get(name, 0) + 1


def _sheet_to_rows(workbook: Workbook, sheet_name: str) -> list[dict[str, Any]]:
    sheet = workbook[sheet_name]
    values = list(sheet.iter_rows(values_only=True))
    if not values:
        return []
    headers = [str(col) if col is not None else "" for col in values[0]]
    rows: list[dict[str, Any]] = []
    for row_values in values[1:]:
        row = {
            header: value
            for header, value in zip(headers, row_values, strict=False)
            if header
        }
        if any(value is not None for value in row.values()):
            rows.append(row)
    return rows


@dataclass
class XlsxEngine:
    """Workbook-backed engine: workbook as DB, sheet names as tables."""

    path: str
    pk: str
    workbook: Workbook
    catalog: WorkbookCatalog


def xlsx_engine(
    *, mapping: dict[str, Any] | None = None, **_: Any
) -> tuple[XlsxEngine, Callable[[], XlsxSession]]:
    config = dict(mapping or {})
    path_value = config.get("path") or config.get("file")
    if not isinstance(path_value, str) or not path_value:
        raise TypeError("mapping['path'] (or 'file') must be a non-empty string")
    path = str(Path(path_value))

    pk = config.get("pk", "id")
    if not isinstance(pk, str) or not pk:
        raise TypeError("mapping['pk'] must be a non-empty string")

    workbook = load_workbook(path)
    if not workbook.sheetnames:
        raise ValueError("workbook must contain at least one sheet")

    catalog = WorkbookCatalog(
        workbook=workbook,
        path=path,
        tables={name: _sheet_to_rows(workbook, name) for name in workbook.sheetnames},
        pks={name: pk for name in workbook.sheetnames},
    )
    engine = XlsxEngine(path=path, pk=pk, workbook=workbook, catalog=catalog)

    def session_factory() -> XlsxSession:
        return XlsxSession(catalog)

    return engine, session_factory


def xlsx_capabilities() -> dict[str, object]:
    return {
        "files": ["xlsx"],
        "workbook_database": True,
        "multi_table": True,
        "workbook_api": ["load_workbook", "wb[...]", "wb.save"],
        "transactions": True,
        "dialect": "xlsx",
    }
