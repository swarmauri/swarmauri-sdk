"""Common JSON-RPC method names used across Peagen components.

.. deprecated:: 0.9.0
   Import method names from :mod:`peagen.protocols` instead.
"""

from __future__ import annotations

import warnings

from peagen.protocols.methods import (
    TASK_SUBMIT as PROTO_TASK_SUBMIT,
    KEYS_UPLOAD as PROTO_KEYS_UPLOAD,
    KEYS_FETCH as PROTO_KEYS_FETCH,
    KEYS_DELETE as PROTO_KEYS_DELETE,
    SECRETS_ADD as PROTO_SECRETS_ADD,
    SECRETS_GET as PROTO_SECRETS_GET,
    SECRETS_DELETE as PROTO_SECRETS_DELETE,
)

warnings.warn(
    "peagen.defaults.methods is deprecated; use peagen.protocols instead",
    DeprecationWarning,
    stacklevel=2,
)

# Worker ↔ Gateway
WORK_START = "Work.start"
WORK_CANCEL = "Work.cancel"
WORK_FINISHED = "Work.finished"
WORKER_REGISTER = "Worker.register"
WORKER_HEARTBEAT = "Worker.heartbeat"
WORKER_LIST = "Worker.list"

# Client ↔ Gateway
TASK_SUBMIT = PROTO_TASK_SUBMIT
TASK_CANCEL = "Task.cancel"
TASK_PAUSE = "Task.pause"
TASK_RESUME = "Task.resume"
TASK_RETRY = "Task.retry"
TASK_RETRY_FROM = "Task.retry_from"
TASK_PATCH = "Task.patch"
TASK_GET = "Task.get"

# Gateway-only
GUARD_SET = "Guard.set"
POOL_CREATE = "Pool.create"
POOL_JOIN = "Pool.join"
POOL_LIST_TASKS = "Pool.listTasks"
KEYS_UPLOAD = PROTO_KEYS_UPLOAD
KEYS_FETCH = PROTO_KEYS_FETCH
KEYS_DELETE = PROTO_KEYS_DELETE
SECRETS_ADD = PROTO_SECRETS_ADD
SECRETS_GET = PROTO_SECRETS_GET
SECRETS_DELETE = PROTO_SECRETS_DELETE

__all__ = [
    "WORK_START",
    "WORK_CANCEL",
    "WORK_FINISHED",
    "WORKER_REGISTER",
    "WORKER_HEARTBEAT",
    "WORKER_LIST",
    "TASK_SUBMIT",
    "TASK_CANCEL",
    "TASK_PAUSE",
    "TASK_RESUME",
    "TASK_RETRY",
    "TASK_RETRY_FROM",
    "TASK_PATCH",
    "TASK_GET",
    "GUARD_SET",
    "POOL_CREATE",
    "POOL_JOIN",
    "POOL_LIST_TASKS",
    "KEYS_UPLOAD",
    "KEYS_FETCH",
    "KEYS_DELETE",
    "SECRETS_ADD",
    "SECRETS_GET",
    "SECRETS_DELETE",
]
