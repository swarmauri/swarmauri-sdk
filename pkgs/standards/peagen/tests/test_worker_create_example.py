from peagen.gateway import app
from fastapi.testclient import TestClient


def test_worker_create_has_example():
    client = TestClient(app)
    schema = client.get("/openapi.json").json()
    worker_schema = schema["components"]["schemas"]["WorkerCreateRequest"]
    assert "example" in worker_schema
    assert worker_schema["properties"].keys() >= {
        "pool_id",
        "url",
        "advertises",
        "handler_map",
    }
    assert worker_schema["example"]["url"] == "http://127.0.0.1:8001/rpc"
