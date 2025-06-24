"""peagen.defaults.events
-----------------------
Default channel and key names for Peagen communication.
"""

CONTROL_QUEUE = "control"
"""Worker ↔ gateway control messages queue."""

READY_QUEUE = "queue"
"""Prefix for per-pool ready queues."""

PUBSUB_CHANNEL = "task:update"
"""Channel name for task event broadcasts."""

TASK_KEY = "task:{}"
"""Redis key template for task metadata."""

__all__ = [
    "CONTROL_QUEUE",
    "READY_QUEUE",
    "PUBSUB_CHANNEL",
    "TASK_KEY",
]
