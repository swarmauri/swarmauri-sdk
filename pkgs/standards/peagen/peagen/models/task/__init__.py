from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .status import Status


class Task(BaseModel):
    """Lightweight task envelope used by the gateway and CLI."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pool: str = "default"
    payload: Dict[str, Any]
    status: Status = Status.waiting
    relations: List[str] = Field(default_factory=list)
    edge_pred: Optional[str] = None
    labels: List[str] = Field(default_factory=list)
    in_degree: int = 0
    config_toml: Optional[str] = None
    commit_hexsha: Optional[str] = None
    oids: Optional[List[str]] = None
    duration: Optional[int] = None


__all__ = ["Task"]
