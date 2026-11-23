from dataclasses import dataclass


@dataclass(frozen=True)
class RunCheckpoint:
    """An opaque serialized run and its optimistic concurrency revision."""

    run_id: str
    revision: int
    payload: str
