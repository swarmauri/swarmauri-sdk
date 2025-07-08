# peagen/worker/base.py
from __future__ import annotations

import asyncio, logging, os, socket, uuid, json
from typing import Any, Awaitable, Callable, Dict, List, Optional, Iterable

import httpx
from fastapi import Body, FastAPI, HTTPException, Request
from pydantic import BaseModel
from peagen.transport import RPCDispatcher
from swarmauri_standard.loggers.Logger import Logger

# ─── AutoAPI & client ────────────────────────────────────────────────
from autoapi_client           import AutoAPIClient
from autoapi.v2               import AutoAPI            # façade for get_schema
from peagen.orm               import Worker, Work

# Auto-generated schemas
SWorkerCreate = AutoAPI.get_schema(Worker, "create")
SWorkerRead   = AutoAPI.get_schema(Worker, "read")
SWorkerUpdate = AutoAPI.get_schema(Worker, "update")

SWorkCreate   = AutoAPI.get_schema(Work,   "create")
SWorkUpdate   = AutoAPI.get_schema(Work,   "update")

# --------------------------------------------------------------------
def _local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


class WorkerBase:
    """
    Minimal worker that registers with an AutoAPI-powered gateway,
    exposes /rpc for Work.start calls and reports progress via
    Works.update.
    """

    # ───────────────────────── constructor ──────────────────────────
    def __init__(
        self,
        *,
        pool: str | None = None,
        gateway: str | None = None,
        host: str | None = None,
        port: int | None = None,
        worker_id: str | None = None,
        log_level: str | None = None,
        heartbeat_interval: float = 5.0,
    ) -> None:

        # ----- env / defaults --------------------------------------
        self.pool      = pool      or os.getenv("DQ_POOL", "default")
        self.gateway   = gateway   or os.getenv("DQ_GATEWAY", "http://localhost:8000/rpc")
        self.worker_id = worker_id or os.getenv("DQ_WORKER_ID", str(uuid.uuid4())[:8])
        self.port      = port      or int(os.getenv("PORT", 8001))
        self.host      = host      or os.getenv("DQ_HOST") or _local_ip()
        self.listen_at = f"http://{self.host}:{self.port}/rpc"

        lvl   = (log_level or os.getenv("DQ_LOG_LEVEL", "INFO")).upper()
        level = getattr(logging, lvl, logging.INFO)
        self.log = Logger(name="worker", default_level=level)

        # ----- runtime objects -------------------------------------
        self.app        = FastAPI(title="Peagen Worker")
        self._handlers: dict[str, Callable[[dict], Awaitable[dict]]] = {}
        self._client    = AutoAPIClient(self.gateway)
        self._http      = httpx.AsyncClient(timeout=10.0)
        self._hb_task: asyncio.Task | None = None
        self._hb_every  = heartbeat_interval
        self.ready      = False

        # ----- built-in JSON-RPC dispatcher ------------------------
        self.rpc = RPCDispatcher()

        @self.rpc.method("Works.create")
        async def _on_work_start(payload: dict) -> dict:
            asyncio.create_task(self._run_work(payload))
            return {"accepted": True}

        # ----- mount FastAPI routes --------------------------------
        @self.app.post("/rpc", response_model=dict)
        async def _rpc_ep(body: dict = Body(...)):
            resp = await self.rpc.dispatch(body)
            return resp

        @self.app.get("/healthz")
        async def _health():
            if self.ready:
                return {"status": "ok"}
            raise HTTPException(503, "starting")

        @self.app.get("/well-known")
        async def _well_known():
            return {"handlers": list(self._handlers)}

        # lifecycle hooks
        @self.app.on_event("startup")
        async def _start():
            await self._startup()

        @self.app.on_event("shutdown")
        async def _stop():
            await self._shutdown()

    # ───────────────────────── public helpers ──────────────────────
    def register_handler(
        self, name: str, func: Callable[[dict], Awaitable[dict]]
    ) -> None:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("handler must be async")
        self._handlers[name] = func
        self.log.info("handler registered: %s", name)

    # ────────────────────── AutoAPI interactions ───────────────────
    async def _startup(self) -> None:
        """
        • Create Worker row (Workers.create)
        • Kick-off heartbeat loop
        """
        try:
            payload = SWorkerCreate(
                id=self.worker_id,
                pool=self.pool,
                url=self.listen_at,
                advertises={"cpu": True},
                handlers=list(self._handlers),
            )
            self._client.call("Workers.create", params=payload, out_schema=SWorkerRead)
            self.log.info("registered @ gateway as %s", self.worker_id)
        except Exception as exc:
            self.log.error("registration failed: %s", exc, exc_info=True)

        # start heartbeat
        self._hb_task = asyncio.create_task(self._heartbeat_loop())
        self.ready = True

    async def _shutdown(self) -> None:
        if self._hb_task:
            self._hb_task.cancel()
        await self._http.aclose()
        self._client.close()

    async def _heartbeat_loop(self):
        while True:
            await asyncio.sleep(self._hb_every)
            try:
                upd = SWorkerUpdate(id=self.worker_id)  # last_seen handled server-side
                self._client.call("Workers.update", params=upd)
                self.log.debug("heartbeat ok")
            except Exception as exc:
                self.log.warning("heartbeat failed: %s", exc)

    # ─────────────────────── work execution flow ───────────────────
    async def _run_work(self, raw: dict) -> None:
        """
        Dispatch *raw* work payload to the appropriate local handler
        and report status back via Works.update.
        """
        try:
            work_in  = SWorkCreate.model_validate(raw)
            task_id  = work_in.id
            action   = (work_in.payload or {}).get("action")

            if action not in self._handlers:
                raise RuntimeError(f"unsupported action '{action}'")

            await self._notify(task_id, "running")

            result = await self._handlers[action](raw)

            await self._notify(task_id, "success", result=result)

        except Exception as exc:
            self.log.exception("work failed: %s", exc)
            await self._notify(raw.get("id", "unknown"), "failed", {"error": str(exc)})

    async def _notify(
        self, work_id: str, status: str, *, result: dict | None = None
    ) -> None:
        try:
            upd = SWorkUpdate(id=work_id, status=status, result=result)
            self._client.call("Works.update", params=upd)
            self.log.info("Works.update %s → %s", work_id, status)
        except Exception as exc:
            self.log.error("notify failed: %s", exc) 