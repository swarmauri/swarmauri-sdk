import os
import uuid
import httpx
import pytest
from peagen.protocols import Request
from peagen.protocols.methods import TASK_SUBMIT

pytestmark = pytest.mark.smoke

GATEWAY = os.environ.get("PEAGEN_TEST_GATEWAY", "https://gw.peagen.com/rpc")


def _gateway_available(url: str) -> bool:
    """Return ``True`` if the gateway RPC endpoint accepts POST requests."""
    envelope = Request(id=0, method="Worker.list", params={}).model_dump()
    try:
        resp = httpx.post(url, json=envelope, timeout=5)
    except Exception:
        return False
    return resp.status_code == 200


@pytest.mark.i9n
def test_worker_list_returns_workers() -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    resp = httpx.post(
        GATEWAY,
        json=Request(id=1, method="Worker.list", params={}).model_dump(),
        timeout=5,
    )
    assert resp.status_code == 200
    assert isinstance(resp.json().get("result"), list)


@pytest.mark.i9n
def test_eval_submit_returns_task_id() -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    task_id = str(uuid.uuid4())
    payload = {
        "action": "eval",
        "args": {
            "workspace_uri": "git+testproject@HEAD",
            "program_glob": "*.py",
        },
    }

    envelope = Request(
        id=task_id,
        method=TASK_SUBMIT,
        params={"pool": "default", "payload": payload, "taskId": task_id},
    ).model_dump()
    resp = httpx.post(GATEWAY, json=envelope, timeout=5)
    assert resp.status_code == 200
    data = resp.json()

    assert "result" in data and "task_id" in data["result"]
