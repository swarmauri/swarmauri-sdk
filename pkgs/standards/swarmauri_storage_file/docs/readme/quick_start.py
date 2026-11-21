from pathlib import Path
import io

from swarmauri_storage_file import FileStorageAdapter

workspace = Path("./artifacts").resolve()
adapter = FileStorageAdapter(output_dir=workspace)

root_uri = adapter.root_uri
print("Root URI:", root_uri)

uri = adapter.upload("example.txt", io.BytesIO(b"hello world"))
print("Stored at:", uri)

downloaded = adapter.download("example.txt").read().decode("utf-8")
print("Contents:", downloaded)

keys = list(adapter.iter_prefix(""))
print("Keys:", keys)
