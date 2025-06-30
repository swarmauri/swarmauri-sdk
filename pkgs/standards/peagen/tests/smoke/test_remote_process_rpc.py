import os
import time
from pathlib import Path

import httpx
import pytest
from peagen.transport.jsonrpc_schemas.worker import WORKER_LIST
from peagen.cli.task_helpers import build_task, submit_task

pytestmark = pytest.mark.smoke

GATEWAY = os.environ.get("PEAGEN_TEST_GATEWAY", "https://gw.peagen.com/rpc")
if not GATEWAY.endswith("/rpc"):
    GATEWAY = GATEWAY.rstrip("/") + "/rpc"
PROJECTS_FILE = (
    Path(__file__).resolve().parent.parent
    / "examples"
    / "projects_payloads"
    / "project_payloads.yaml"
)
REPO = "testproject"


def _gateway_available(url: str) -> bool:
    """Return ``True`` if the gateway RPC endpoint accepts POST requests."""
    envelope = {"jsonrpc": "2.0", "method": WORKER_LIST, "params": {}, "id": 0}
    try:
        response = httpx.post(url, json=envelope, timeout=5)
    except Exception:
        return False
    return response.status_code < 500


@pytest.mark.i9n
def test_rpc_submit_remote_process(tmp_path: Path) -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    payload_text = PROJECTS_FILE.read_text(encoding="utf-8")
    task = build_task(
        "process",
        {"projects_payload": payload_text, "repo": REPO, "ref": "HEAD"},
    )
    reply = submit_task(GATEWAY, task)
    if "error" in reply:
        pytest.skip(f"remote submit failed: {reply['error']['message']}")
    assert "result" in reply and "id" in reply["result"]


@pytest.mark.i9n
def test_rpc_watch_remote_process(tmp_path: Path) -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    payload_text = PROJECTS_FILE.read_text(encoding="utf-8")
    task = build_task(
        "process",
        {"projects_payload": payload_text, "repo": REPO, "ref": "HEAD"},
    )
    reply = submit_task(GATEWAY, task)
    if "error" in reply:
        pytest.skip(f"remote submit failed: {reply['error']['message']}")

    tid = reply.get("result", {}).get("id")
    assert tid

    envelope = {
        "jsonrpc": "2.0",
        "method": "Task.get",
        "params": {"taskId": tid},
        "id": 1,
    }
    status = None
    for _ in range(30):
        result = httpx.post(GATEWAY, json=envelope, timeout=30).json()["result"]
        status = result["status"]
        if status in {"success", "failed", "rejected", "cancelled"}:
            break
        time.sleep(2)
    assert status in {"success", "failed", "rejected", "cancelled"}
