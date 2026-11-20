import io

from swarmauri_storage_memory import MemoryStorageAdapter

adapter = MemoryStorageAdapter(prefix="session")

uri = adapter.upload("example.txt", io.BytesIO(b"hello"))
print("Stored at:", uri)

downloaded = adapter.download("example.txt").read().decode("utf-8")
print("Contents:", downloaded)

keys = list(adapter.iter_prefix(""))
print("Keys:", keys)
