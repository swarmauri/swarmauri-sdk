"""Common JSON-RPC method names used across Peagen components."""

# Worker ↔ Gateway
WORK_START = "Work.start"
WORK_CANCEL = "Work.cancel"
WORK_FINISHED = "Work.finished"
WORKER_REGISTER = "Worker.register"
WORKER_HEARTBEAT = "Worker.heartbeat"
WORKER_LIST = "Worker.list"

# Client ↔ Gateway
TASK_SUBMIT = "Task.submit"
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
KEYS_UPLOAD = "Keys.upload"
KEYS_FETCH = "Keys.fetch"
KEYS_DELETE = "Keys.delete"
SECRETS_ADD = "Secrets.add"
SECRETS_GET = "Secrets.get"
SECRETS_DELETE = "Secrets.delete"

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
