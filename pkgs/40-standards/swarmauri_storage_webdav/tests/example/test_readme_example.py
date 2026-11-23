import httpx

from swarmauri_storage_webdav import WebDAVStorageAdapter


def test_readme_round_trip() -> None:
    objects: dict[str, bytes] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "MKCOL":
            return httpx.Response(201)
        if request.method == "PUT":
            objects[request.url.path] = request.content
            return httpx.Response(201)
        if request.method == "GET":
            return httpx.Response(200, content=objects[request.url.path])
        return httpx.Response(405)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    storage = WebDAVStorageAdapter(
        base_url="https://dav.example.test/files/jacob/",
        prefix="artifacts",
        client=client,
    )

    uri = storage.put_blob("runs/42/result.json", b'{"status":"complete"}')

    assert uri.endswith("/artifacts/runs/42/result.json")
    assert storage.get_blob("runs/42/result.json") == b'{"status":"complete"}'
