"""
dqueue.worker.server
────────────────────
FastAPI-based worker that speaks JSON-RPC 2.0 and logs *everything*.
"""
print('DEPRECATED. THIS WILL BE REMOVED ASAP.')


from __future__ import annotations

import asyncio, logging, os, time, uuid, json
from json.decoder import JSONDecodeError
from typing import Any, Dict, Optional

from fastapi import Body, FastAPI, Request, Response
import httpx

from ..models import Status
from ..transport.jsonrpc import RPCDispatcher
from ..transport.schemas import RPCRequest, RPCResponse
import socket


# ──────────────────────────── utils  ────────────────────────────
def get_local_ip():
    # open a dummy socket to some known public host and get your own IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0] 
    finally:
        s.close()


# ──────────────────────────── logging  ────────────────────────────
LOG_LEVEL = os.getenv("DQ_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)5s] %(name)s: %(message)s",
)

log = logging.getLogger("uvicorn")

# silence noisy deps but keep warnings
logging.getLogger("httpx").setLevel("WARNING")
logging.getLogger("uvicorn.error").setLevel("INFO")

# ──────────────────────────── globals  ────────────────────────────
POOL        = os.getenv("DQ_POOL", "default")
DQ_GATEWAY = os.getenv("DQ_GATEWAY", "http://localhost:8000/rpc")
WORKER_ID   = os.getenv("DQ_WORKER_ID", str(uuid.uuid4())[:8])
PORT        = int(os.getenv("PORT", "9001"))
HOST        = os.getenv("DQ_HOST", "localhost")
if not HOST:
    HOST = get_local_ip()

LISTEN_PATH = "/rpc"  # exposed endpoint


url_self = f"http://{HOST}:{PORT}{LISTEN_PATH}"

app = FastAPI(title="DQueue Worker")
rpc = RPCDispatcher()

_client: Optional[httpx.AsyncClient] = None  # set on startup

# ──────────────────────────── rpc endpoint ────────────────────────
@app.post(
    LISTEN_PATH,
    response_model=RPCResponse,
    response_model_exclude_none=True,
    summary="JSON-RPC 2.0 endpoint",
)
async def rpc_endpoint(
    request: Request,
    body: RPCRequest = Body(..., description="JSON-RPC 2.0 envelope"),
):
    # auto-assign id when omitted
    if body.id is None:
        body.id = str(uuid.uuid4())

    payload = body.model_dump()
    log.debug("RPC  ←  %s", payload)

    resp = await rpc.dispatch(payload)

    if resp.get("error"):
        log.warning("%s error → %s", body.method, resp["error"])
    else:
        log.debug("RPC  →  %s", resp)

    return resp


# ──────────────────────────── Work RPCs ───────────────────────────
@rpc.method("Work.start")
async def work_start(task: Dict[str, Any]):
    """Kick off async job and return immediately."""
    log.info("Work.start received  task=%s pool=%s", task.get("id"), POOL)
    asyncio.create_task(_run_task(task))
    return {"accepted": True}


@rpc.method("Work.cancel")
def work_cancel(taskId: str):
    log.info("Work.cancel received  task=%s", taskId)
    # demo worker: no real cancellation yet
    return {"ok": True}


# ────────────────────────── task execution ────────────────────────
async def _run_task(task: Dict[str, Any]):
    await _notify("running", task["id"])
    await asyncio.sleep(2)  # simulate workload
    result = {"echo": task["payload"]}
    await _notify("success", task["id"], result)


async def _notify(state: str, task_id: str, result: Dict[str, Any] | None = None):
    if _client is None:
        raise RuntimeError("HTTP client not initialized")

    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "Work.finished",
        "params": {"taskId": task_id, "status": state, "result": result},
    }
    await _client.post(DQ_GATEWAY, json=payload)
    log.info("Work.finished sent    task=%s state=%s", task_id, state)


# ─────────────────────────────── Healthcheck ───────────────────────────────
@app.get("/health", tags=["health"])
async def health() -> dict:
    """
    Simple readiness probe. Returns 200 OK as long as the app is running.
    Docker’s healthcheck will curl this endpoint.
    """
    return {"status": "ok"}

# ──────────────────────────── startup  ────────────────────────────
@app.on_event("startup")
async def _startup():
    """Register worker and start heartbeat."""
    global _client
    _client = httpx.AsyncClient(timeout=10)

    async def _send_rpc(method: str, params: Dict[str, Any]):
        body = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": method,
            "params": params,
        }
        await _client.post(DQ_GATEWAY, json=body)
        log.debug("sent %s → %s", method, params)

    # ───── register
    await _send_rpc(
        "Worker.register",
        {
            "workerId": WORKER_ID,
            "pool": POOL,
            "url": url_self,
            "advertises": {"cpu": True},
        },
    )
    log.info("registered  id=%s pool=%s url=%s", WORKER_ID, POOL, url_self)

    # ───── heartbeat
    async def _heartbeat():
        while True:
            try:
                await _send_rpc(
                    "Worker.heartbeat",
                    {
                        "workerId": WORKER_ID,
                        "pool": POOL,
                        "url": url_self,
                        "metrics": {},
                    },
                )
                log.debug("heartbeat ok")
            except Exception as exc:
                log.warning("heartbeat failed: %s", exc)
            await asyncio.sleep(5)

    asyncio.create_task(_heartbeat())


# ──────────────────────────── shutdown  ───────────────────────────
@app.on_event("shutdown")
async def _shutdown():
    if _client:
        await _client.aclose()
        log.info("HTTP client closed")
