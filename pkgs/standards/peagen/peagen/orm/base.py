import uuid
from datetime import datetime

from sqlalchemy import DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

Base = declarative_base()

# ────────────────────────────  helpers  ────────────────────────────
#: server-side expression that returns a *naïve* UTC timestamp
# Use CURRENT_TIMESTAMP for compatibility across different databases
UTC_NOW = text("CURRENT_TIMESTAMP")


# ────────────────────────────  mixins  ─────────────────────────────
class UUIDMixin:
    """Provides a UUID primary-key column."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class TimestampMixin:
    """Stores created / modified in UTC *without* tzinfo."""

    date_created: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),  # → TIMESTAMP WITHOUT TIME ZONE
        server_default=UTC_NOW,
        nullable=False,
    )
    last_modified: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=UTC_NOW,
        server_onupdate=UTC_NOW,
        nullable=False,
    )


class BaseModel(Base, UUIDMixin, TimestampMixin):
    """Base for all models."""

    __abstract__ = True
