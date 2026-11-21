from swarmauri_storage_webdav import WebDAVStorageAdapter

with WebDAVStorageAdapter(
    base_url="https://dav.example.com/remote.php/dav/files/jacob/",
    username="jacob",
    password="secret",
    prefix="artifacts",
) as storage:
    storage.put_blob("runs/42/result.json", b'{"status":"complete"}')
    payload = storage.get_blob("runs/42/result.json")

    storage.push("./dist", prefix="releases/0.1.0")
    storage.pull("releases/0.1.0", "./download")

    print(storage.capabilities())
    print(payload)
