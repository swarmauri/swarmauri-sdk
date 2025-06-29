"""Convenience accessors for gateway RPC handlers."""

from __future__ import annotations

__all__ = [
    "keys_upload",
    "keys_fetch",
    "keys_delete",
    "pool_create",
    "pool_join",
    "pool_list",
    "task_submit",
    "task_cancel",
    "task_pause",
    "task_resume",
    "task_retry",
    "task_retry_from",
    "guard_set",
    "secrets_add",
    "secrets_get",
    "secrets_delete",
    "task_patch",
    "task_get",
    "worker_register",
    "worker_heartbeat",
    "worker_list",
    "work_finished",
]


def __getattr__(name: str):
    if name in __all__:
        from . import keys, pool, secrets, tasks, workers

        modules = {
            "keys_upload": keys,
            "keys_fetch": keys,
            "keys_delete": keys,
            "pool_create": pool,
            "pool_join": pool,
            "pool_list": pool,
            "task_submit": tasks,
            "task_cancel": tasks,
            "task_pause": tasks,
            "task_resume": tasks,
            "task_retry": tasks,
            "task_retry_from": tasks,
            "guard_set": tasks,
            "secrets_add": secrets,
            "secrets_get": secrets,
            "secrets_delete": secrets,
            "task_patch": tasks,
            "task_get": tasks,
            "worker_register": workers,
            "worker_heartbeat": workers,
            "worker_list": workers,
            "work_finished": workers,
        }
        module = modules[name]
        return getattr(module, name)
    raise AttributeError(name)
