from fastapi.testclient import TestClient
from dqueue.transport.http_api import app

client = TestClient(app)


def test_pool_lifecycle():
    r = client.post("/pools/alpha")
    assert r.status_code == 200
    task = client.post("/pools/alpha/tasks", json={"x": 1}).json()
    assert task["status"] == "pending"
