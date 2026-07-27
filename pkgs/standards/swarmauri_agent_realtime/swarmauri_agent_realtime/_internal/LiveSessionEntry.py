import asyncio
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LiveSessionEntry:
    conversation_id: str
    creation_task: asyncio.Task[Any]
    session: Any | None = None
    leases: int = 0
    last_used_at: float = field(default=0.0)
    invalidated: bool = False
