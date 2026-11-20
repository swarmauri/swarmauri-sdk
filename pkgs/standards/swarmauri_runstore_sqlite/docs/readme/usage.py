from swarmauri_core.run_stores import RunCheckpoint
from swarmauri_runstore_sqlite import SqliteRunStore

store = SqliteRunStore(path="runs.db")
store.create(RunCheckpoint("example", 0, '{"status":"ready"}'))
checkpoint = store.load("example")
print(store.save(checkpoint).revision)
