from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Mapping, Optional, Tuple
import threading

import pandas as pd

from tigrbl.session.spec import SessionSpec
from .df_session import TransactionalDataFrameSession

# ---- Engine object: in-memory catalog of DataFrames + versions ----

@dataclass
class DataFrameCatalog:
    tables: Dict[str, pd.DataFrame] = field(default_factory=dict)   # name -> live frame
    pks: Dict[str, str] = field(default_factory=dict)               # name -> primary-key column
    table_ver: Dict[str, int] = field(default_factory=dict)         # name -> monotonic version
    lock: threading.RLock = field(default_factory=threading.RLock)  # atomic apply on commit

    def get_live(self, name: str) -> pd.DataFrame:
        if name not in self.tables:
            self.tables[name] = pd.DataFrame()
            self.table_ver[name] = 0
        self.table_ver.setdefault(name, 0)
        return self.tables[name]

    def bump(self, name: str) -> None:
        self.table_ver[name] = self.table_ver.get(name, 0) + 1


# ---- Builder expected by Tigrbl EngineSpec (kind='dataframe') ----

def dataframe_engine(
    *,
    mapping: Optional[Mapping[str, object]] = None,
    spec: Any = None,
    dsn: Optional[str] = None,
) -> Tuple[DataFrameCatalog, Callable[[], TransactionalDataFrameSession]]:
    """
    Return (engine, sessionmaker) for the 'dataframe' kind.

    EngineSpec(kind="dataframe") calls this with:
      - mapping: plugin-specific config (tables, pks)
      - spec: the EngineSpec instance (not used here)
      - dsn: optional DSN (not used here)
    """
    m = dict(mapping or {})
    initial_tables = m.get("tables") or {}
    pks = m.get("pks") or {}

    if not isinstance(initial_tables, dict):
        raise TypeError("mapping['tables'] must be a dict[str, pandas.DataFrame]")
    if not isinstance(pks, dict):
        raise TypeError("mapping['pks'] must be a dict[str, str]")

    # Defensive copy of tables
    tables = {k: (v.copy() if isinstance(v, pd.DataFrame) else v) for k, v in initial_tables.items()}
    cat = DataFrameCatalog(tables=tables, pks=dict(pks))

    def mk() -> TransactionalDataFrameSession:
        # A neutral SessionSpec is attached here; the effective SessionSpec from
        # session_ctx is typically applied by the Tigrbl layer wrapping the sessionmaker.
        return TransactionalDataFrameSession(cat, spec=SessionSpec())

    return cat, mk


# ---- Capabilities (optional but useful for validation) ----

def dataframe_capabilities() -> dict[str, object]:
    """Report capabilities for the 'dataframe' engine."""
    return {
        "transactional": True,
        "read_only_enforced": True,
        "isolation_levels": {"read_committed", "repeatable_read", "snapshot", "serializable"},
    }
