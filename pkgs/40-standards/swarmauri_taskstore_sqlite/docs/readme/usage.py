import time
from swarmauri_core.permissions import Permission
from swarmauri_core.tasks import TaskRecord
from swarmauri_taskstore_sqlite import SqliteTaskStore

store = SqliteTaskStore(path="tasks.db")
store.create(
    TaskRecord(
        "report-1",
        "user:alice",
        "acme",
        (Permission("documents:read", "document:123", "acme"),),
        int(time.time()) + 600,
    )
)
assert store.load("report-1").subject == "user:alice"
