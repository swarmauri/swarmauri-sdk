"""
tests/test_worker_crud.py
End-to-end CRUD check for the Worker table.

Requires:
    • A running gateway at http://127.0.0.1:8000/v1
    • pytest
    • The TigrblClient helper shipped with Peagen/AutoTigrbl
"""

import uuid
import httpx
import pytest

# ❶ ------------------------------------------------------------------------
# Runtime wiring
from tigrbl import get_schema  # your AutoTigrbl import
from peagen.orm import Worker  # ORM class
from peagen.defaults import DEFAULT_POOL_ID
from tigrbl_client import TigrblClient  # JSON-RPC helper

# GATEWAY_RPC = "https://gw.peagen.com/rpc"
GATEWAY_RPC = "http://127.0.0.1:8000/rpc"


def _gateway_available(url: str) -> bool:
    """Return ``True`` if the gateway RPC endpoint accepts POST requests."""
    envelope = {"jsonrpc": "2.0", "method": "Worker.list", "params": {}, "id": 0}
    try:
        response = httpx.post(url, json=envelope, timeout=5)
    except Exception:
        return False
    return response.status_code == 200


# ❷ ------------------------------------------------------------------------
# Schemas generated on-the-fly so the test never drifts from the server
SWorkerCreate = get_schema(Worker, "create")
SWorkerUpdate = get_schema(Worker, "update")
SWorkerRead = get_schema(Worker, "read")


# ❸ ------------------------------------------------------------------------
@pytest.mark.i9n
def test_worker_create_and_update():
    if not _gateway_available(GATEWAY_RPC):
        pytest.skip("gateway not reachable")
    worker_id = str(uuid.uuid4())
    print(worker_id, type(worker_id), str(DEFAULT_POOL_ID), type(str(DEFAULT_POOL_ID)))
    create_payload = SWorkerCreate(
        id=worker_id,
        pool_id=str(DEFAULT_POOL_ID),  # or omit if server fills
        url="http://worker-test:9000",
        handlers={"doe": True, "evolve": True},
        advertises={"cpu": 4, "ram_gb": 8},
    )
    print(create_payload)
    with TigrblClient(GATEWAY_RPC) as c:
        # --- CREATE -------------------------------------------------------
        created = c.call(
            "Worker.create",
            params=create_payload,
            out_schema=SWorkerRead,
        )
        assert created.id == str(worker_id)
        assert created.url == create_payload.url
        assert created.handlers == create_payload.handlers

        # --- UPDATE (heartbeat-like) -------------------------------------
        upd_payload = SWorkerUpdate(
            id=str(worker_id),
            handlers={"doe": True, "evolve": True, "fetch": True},
            advertises={"cpu": 8, "ram_gb": 16},
            # pool_id omitted → immutable (info={"no_update": True})
        )
        updated = c.call(
            "Worker.update",
            params=upd_payload,
            out_schema=SWorkerRead,
        )
        assert "fetch" in updated.handlers
        assert updated.advertises["cpu"] == 8

        # --- READ back ----------------------------------------------------
        reread = c.call(
            "Worker.read",
            params={"id": worker_id},
            out_schema=SWorkerRead,
        )
        assert reread.handlers == updated.handlers
        assert reread.advertises == updated.advertises

        # --- LIST filter --------------------------------------------------
        listed = c.call(
            "Worker.list",
            params={"skip": 0, "limit": 10},
        )
        assert any(w["id"] == str(worker_id) for w in listed)
