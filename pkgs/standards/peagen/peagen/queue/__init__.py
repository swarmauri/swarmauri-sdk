from __future__ import annotations

from peagen.plugin_registry import registry
from .base import TaskQueue


def make_queue(provider: str, **kwargs) -> TaskQueue:
    try:
        cls = registry["task_queues"][provider]
    except KeyError:
        raise ValueError(f"No TaskQueue registered for provider '{provider}'")
    return cls(**kwargs)


def __getattr__(name: str):
    if name == "TaskQueue":
        return TaskQueue
    raise AttributeError(name)
