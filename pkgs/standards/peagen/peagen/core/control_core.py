"""Core helpers for task control-plane operations."""

from __future__ import annotations

from typing import Iterable

from peagen.orm import Status, Task
from tigrbl.v3 import get_schema

SUpdate = get_schema(Task, "update")


def pause(tasks: Iterable[SUpdate]) -> int:
    selected = list(tasks)
    for t in selected:
        t.status = Status.paused
    return len(selected)


def resume(tasks: Iterable[SUpdate]) -> int:
    selected = list(tasks)
    for t in selected:
        t.status = Status.waiting
    return len(selected)


def cancel(tasks: Iterable[SUpdate]) -> int:
    selected = list(tasks)
    for t in selected:
        t.status = Status.cancelled
    return len(selected)


def retry(tasks: Iterable[SUpdate]) -> int:
    selected = list(tasks)
    for t in selected:
        t.status = Status.queued
    return len(selected)


# retry_from behaves like retry for now
retry_from = retry
