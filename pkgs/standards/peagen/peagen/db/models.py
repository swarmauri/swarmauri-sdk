from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
from uuid import UUID

from peagen.models.schemas import Status


@dataclass(slots=True)
class TaskRevision:
    """Typed representation of a row in ``task_revision``."""

    rev_hash: str
    task_id: UUID
    parent_hash: Optional[str] = None
    ts_created: datetime = field(default_factory=datetime.utcnow)


@dataclass(slots=True)
class ArtefactLineage:
    """Typed representation of a row in ``artefact_lineage``."""

    edge_hash: str
    parent_hash: str
    child_hash: str
    ts_logged: datetime = field(default_factory=datetime.utcnow)


@dataclass(slots=True)
class FanoutSet:
    """Typed representation of a row in ``fanout_set``."""

    rev_hash: str
    child_hash: str
    ts_logged: datetime = field(default_factory=datetime.utcnow)


@dataclass(slots=True)
class StatusLog:
    """Typed representation of a row in ``status_log``."""

    rev_hash: str
    status: Status
    ts_logged: datetime = field(default_factory=datetime.utcnow)


__all__ = [
    "TaskRevision",
    "ArtefactLineage",
    "FanoutSet",
    "StatusLog",
    "asdict",
]
