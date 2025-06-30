import os
import httpx
import pytest
from peagen.transport.jsonrpc_schemas.worker import WORKER_LIST
from peagen.cli.task_helpers import build_task, submit_task

pytestmark = pytest.mark.smoke

GATEWAY = os.environ.get("PEAGEN_TEST_GATEWAY", "https://gw.peagen.com/rpc")


def _gateway_available(url: str) -> bool:
    """Return ``True`` if the gateway RPC endpoint accepts POST requests."""
    envelope = {"jsonrpc": "2.0", "method": WORKER_LIST, "params": {}, "id": 0}
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
        json={"jsonrpc": "2.0", "method": WORKER_LIST, "params": {}, "id": 1},
        timeout=5,
    )
    assert resp.status_code == 200
    assert isinstance(resp.json().get("result"), list)


@pytest.mark.i9n
def test_eval_submit_returns_task_id() -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    task = build_task(
        "eval",
        {
            "workspace_uri": "git+testproject@HEAD",
            "program_glob": "*.py",
        },
    )
    reply = submit_task(GATEWAY, task)
    if "error" in reply:
        pytest.skip(f"remote submit failed: {reply['error']['message']}")

    assert "result" in reply and "id" in reply["result"]
