# ── Standard Library ─────────────────────────────────────────────────────
from __future__ import annotations

from typing import Any
import uuid

# ── Third-party Dependencies ────────────────────────────────────────────
from sqlalchemy.types import TypeDecorator

# ── Local Package ───────────────────────────────────────────────────────
from ..deps.sqlalchemy import String, _PgUUID


class PgUUID(_PgUUID):
    @property
    def hex(self):
        return self.as_uuid.hex


class SqliteUUID(TypeDecorator):
    """UUID type that stores hyphenated strings on SQLite to avoid numeric coercion."""

    impl = String(36)
    cache_ok = True

    def __init__(self, as_uuid: bool = True):
        super().__init__()
        self.as_uuid = as_uuid

    @property
    def python_type(self) -> type:
        return uuid.UUID if self.as_uuid else str

    def load_dialect_impl(self, dialect) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PgUUID(as_uuid=self.as_uuid))
        return dialect.type_descriptor(String(36))

    def process_bind_param(self, value: Any, dialect) -> Any:
        if value is None:
            return None
        if self.as_uuid:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(str(value))
            return value if dialect.name == "postgresql" else str(value)
        return str(value)

    def process_result_value(self, value: Any, dialect) -> Any:
        if value is None:
            return None
        if self.as_uuid:
            if isinstance(value, uuid.UUID):
                return value
            return uuid.UUID(str(value))
        return str(value)
