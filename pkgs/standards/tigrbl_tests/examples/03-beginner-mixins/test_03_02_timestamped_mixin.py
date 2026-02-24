from __future__ import annotations

from tigrbl import Base
from tigrbl.orm.mixins import Timestamped
from tigrbl.types import TZDateTime


def test_timestamped_mixin_columns() -> None:
    class LogEntry(Base, Timestamped):
        __tablename__ = "log_entries"

    assert LogEntry.created_at.storage.type_ is TZDateTime
    assert LogEntry.updated_at.storage.type_ is TZDateTime
