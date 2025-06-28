# peagen/worker/base.py

from __future__ import annotations

import asyncio
import logging
from swarmauri_standard.loggers.Logger import Logger
import os
import socket
import uuid
from typing import Any, Awaitable, Callable, Dict, List, Optional

from pydantic import BaseModel

import httpx
from fastapi import Body, FastAPI, Request, HTTPException
from json.decoder import JSONDecodeError

from peagen.transport import RPCDispatcher, RPCRequest, RPCResponse
from peagen.protocols import Request as RPCEnvelope
from peagen.defaults import WORK_CANCEL, WORK_FINISHED, WORK_START
from peagen.protocols.methods.worker import (
    WORKER_HEARTBEAT,
    WORKER_REGISTER,
    HeartbeatParams,
    RegisterParams,
)
from peagen._utils.config_loader import resolve_cfg
from peagen.plugins import PluginManager
from peagen.errors import HTTPClientNotInitializedError
from peagen.handlers import ensure_task
from peagen.schemas import TaskRead


# ──────────────────────────── utils  ────────────────────────────
def get_local_ip() -> str:
    """
    Open a dummy socket to a known public host and return your own IP.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        # Fall back to localhost if we cannot open a UDP socket (e.g. in
        # restricted CI environments without network access).
        return "127.0.0.1"
    finally:
        s.close()


# ──────────────────────────── WorkBase class  ────────────────────────────
class WorkerBase:
    """
    A reusable base worker that:
      • Exposes /rpc as a JSON-RPC 2.0 endpoint
      • Implements Work.start, Work.cancel
      • Has a healthcheck (/healthz)
      • Sends Worker.register + Worker.heartbeat on startup
      • Sends Work.finished via _notify(...)
      • Allows registering custom handlers via register_handler(name, coro)
      • Exposes GET /well-known → { "handlers": [<registered names>] }
    """

    def __init__(
        self,
        *,
        pool: str = None,
        gateway: str = None,
        host: str = None,
        port: int = None,
        worker_id: str = None,
        log_level: str = None,
    ):
        """
        Initialize environment from ENV or fallbacks:

        ENV:
          • DQ_POOL          (default: "default")
          • DQ_GATEWAY       (default: "http://localhost:8000/rpc")
          • DQ_WORKER_ID     (default: random 8‐char prefix)
          • DQ_HOST          (default: local IP)
          • PORT             (default: 8001)
          • DQ_LOG_LEVEL     (default: "INFO")
        """
        # ─── CONFIGURE from ENV or parameters ────────────────────────
        self.POOL = pool or os.getenv("DQ_POOL", "default")
        self.DQ_GATEWAY = gateway or os.getenv(
            "DQ_GATEWAY", "http://localhost:8000/rpc"
        )
        self.WORKER_ID = worker_id or os.getenv("DQ_WORKER_ID", str(uuid.uuid4())[:8])
        self.PORT = port or int(os.getenv("PORT", "8001"))
        env_host = host or os.getenv("DQ_HOST", "")
        if not env_host:
            env_host = get_local_ip()
        self.HOST = env_host

        # ─── LOGGING ─────────────────────────────────────────────────
        lvl = (log_level or os.getenv("DQ_LOG_LEVEL", "INFO")).upper()
        log_level_int = getattr(logging, lvl, logging.INFO)
        self.log = Logger(name="uvicorn", default_level=log_level_int)

        # Silence overly‐verbose libraries but keep warnings:
        logging.getLogger("httpx").setLevel("WARNING")
        logging.getLogger("uvicorn.error").setLevel("INFO")

        # ─── URLS & FastAPI / RPCDispatcher ──────────────────────────
        self.LISTEN_PATH = "/rpc"
        self.url_self = f"http://{self.HOST}:{self.PORT}{self.LISTEN_PATH}"

        self.app = FastAPI(title="Peagen Worker")
        self.rpc = RPCDispatcher()
        self._client: Optional[httpx.AsyncClient] = None
        self.ready = False

        # ─── Handlers registry: name (str) → async function(task: Dict)→Dict ─
        self._handler_registry: Dict[
            str, Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]
        ] = {}

        # ─── REGISTER built‐in RPC methods ──────────────────────────
        # 1) Work.start  →  on_work_start (async)
        @self.rpc.method(WORK_START)
        async def on_work_start(task: Dict[str, Any]) -> Dict[str, Any]:
            canonical = ensure_task(task)
            self.log.info(
                "Work.start received    task=%s pool=%s", canonical.id, self.POOL
            )
            # Launch the real work in the background
            asyncio.create_task(self._run_task(canonical))
            return {"accepted": True}

        # 2) Work.cancel → calls work_cancel (sync or async)
        @self.rpc.method(WORK_CANCEL)
        async def on_work_cancel(taskId: str) -> Dict[str, Any]:
            self.log.info("Work.cancel received   task=%s", taskId)
            # (Demo worker: you can override this in a subclass if needed)
            return {"ok": True}

        # ─── MOUNT /rpc endpoint for JSON-RPC ────────────────────────
        @self.app.post(
            self.LISTEN_PATH,
            response_model=RPCResponse,
            response_model_exclude_none=True,
            summary="JSON-RPC 2.0 endpoint",
        )
        async def rpc_endpoint(
            request: Request,
            body: RPCRequest = Body(..., description="JSON-RPC 2.0 envelope"),
        ) -> Dict[str, Any]:
            # Auto-assign id if omitted
            if body.id is None:
                body.id = str(uuid.uuid4())
            payload = body.model_dump()
            self.log.debug("RPC  ←  %s", payload)
            try:
                resp = await self.rpc.dispatch(payload)
            except JSONDecodeError as e:
                # Malformed JSON-RPC
                return {
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": str(e)},
                    "id": body.id,
                }
            if resp.get("error"):
                self.log.warning("%s error → %s", body.method, resp["error"])
            else:
                self.log.debug("RPC  →  %s", resp)
            return resp

        # ─── HEALTHCHECK ───────────────────────────────────────────
        @self.app.get("/healthz", tags=["health"])
        async def health() -> Dict[str, str]:
            if self.ready:
                return {"status": "ok"}
            raise HTTPException(status_code=503, detail="starting")

        # ─── WELL‐KNOWN: return registered handler names ─────────────
        @self.app.get("/well-known")
        async def well_known() -> Dict[str, List[str]]:
            return {"handlers": self.supported_handlers()}

        # ─── STARTUP & SHUTDOWN events ──────────────────────────────
        @self.app.on_event("startup")
        async def _startup() -> None:
            await self._on_startup()

        @self.app.on_event("shutdown")
        async def _shutdown() -> None:
            await self._on_shutdown()

    # ──────────────────────────── Public API ────────────────────────────
    def register_handler(
        self,
        handler_name: str,
        handler_func: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]],
    ) -> None:
        """
        Register an async function to handle tasks whose payload["action"] == handler_name.
        The handler must be declared as: async def handler(task: Dict[str,Any]) -> Dict[str,Any].
        """
        if not asyncio.iscoroutinefunction(handler_func):
            raise ValueError(f"Handler for '{handler_name}' must be async")
        self._handler_registry[handler_name] = handler_func
        self.log.info("Registered handler '%s'", handler_name)

    def supported_handlers(self) -> List[str]:
        """Return the list of registered handler names."""
        return list(self._handler_registry.keys())

    # ───────────────────────── Dispatch & Task Execution ─────────────────────────
    async def _run_task(self, task: TaskRead | Dict[str, Any]) -> None:
        """Execute *task* by dispatching to a registered handler."""
        canonical = ensure_task(task)
        task_id = canonical.id
        payload = canonical.payload
        action = payload.get("action")

        if action not in self._handler_registry:
            await self._notify(
                "failed", task_id, {"error": f"Unsupported handler '{action}'"}
            )
            return

        handler = self._handler_registry[action]
        # Immediately tell gateway we’re “running”
        await self._notify("running", task_id)

        try:
            result: Dict[str, Any] = await handler(canonical)
            try:
                cfg = resolve_cfg()
                pm = PluginManager(cfg)
                vcs = pm.get("vcs")
                try:
                    branch = vcs.repo.active_branch.name
                except Exception:
                    branch = "HEAD"
                vcs.push(branch)
            except Exception as exc:
                self.log.warning("VCS push failed: %s", exc)
            status = result.pop("_final_status", "success")
            await self._notify(status, task_id, result)
        except Exception as exc:
            await self._notify("failed", task_id, {"error": str(exc)})

    # ────────────────────────── Internal: send Work.finished ───────────────────────
    async def _notify(
        self, state: str, task_id: str, result: Dict[str, Any] | None = None
    ) -> None:
        """
        Send a Work.finished (or status update) back to the gateway.
        state ∈ {"running", "success", "failed"}.
        """
        if self._client is None:
            raise HTTPClientNotInitializedError()

        payload = RPCEnvelope(
            id=str(uuid.uuid4()),
            method=WORK_FINISHED,
            params={"taskId": task_id, "status": state, "result": result},
        ).model_dump()
        try:
            await self._client.post(self.DQ_GATEWAY, json=payload)
            self.log.info("Work.finished sent    task=%s state=%s", task_id, state)
        except Exception as exc:
            self.log.error("Failed to send Work.finished for %s: %s", task_id, exc)

    # ───────────────────────── Startup / Heartbeat / Shutdown ──────────────────────
    async def _send_rpc(self, method: str, params: BaseModel | Dict[str, Any]) -> None:
        """Send a typed JSON-RPC call to the gateway."""
        if self._client is None:
            raise HTTPClientNotInitializedError()

        payload = params.model_dump() if isinstance(params, BaseModel) else params
        body = RPCEnvelope(
            id=str(uuid.uuid4()), method=method, params=payload
        ).model_dump()
        try:
            await self._client.post(self.DQ_GATEWAY, json=body)
            self.log.debug("sent %s → %s", method, payload)
        except Exception as exc:
            self.log.warning("Failed sending %s to gateway: %s", method, exc)

    async def _on_startup(self) -> None:
        """
        Called when FastAPI starts. Initialize HTTP client, register worker, start heartbeat.
        """
        self._client = httpx.AsyncClient(timeout=10)

        # ───── Worker.register ─────────────────────────────────────
        await self._send_rpc(
            WORKER_REGISTER,
            RegisterParams(
                workerId=self.WORKER_ID,
                pool=self.POOL,
                url=self.url_self,
                advertises={"cpu": True},
                handlers=self.supported_handlers(),
            ),
        )
        self.log.info(
            "registered  id=%s pool=%s url=%s", self.WORKER_ID, self.POOL, self.url_self
        )

        # ───── Heartbeat loop ─────────────────────────────────────
        async def _heartbeat_loop() -> None:
            while True:
                await asyncio.sleep(5)
                try:
                    await self._send_rpc(
                        WORKER_HEARTBEAT,
                        HeartbeatParams(
                            workerId=self.WORKER_ID,
                            pool=self.POOL,
                            url=self.url_self,
                            metrics={},
                        ),
                    )
                    self.log.debug("heartbeat ok")
                except Exception as exc:
                    self.log.warning("heartbeat failed: %s", exc)

        asyncio.create_task(_heartbeat_loop())
        self.ready = True

    async def _on_shutdown(self) -> None:
        """
        Called when FastAPI shuts down. Close HTTP client.
        """
        if self._client:
            await self._client.aclose()
            self.log.info("HTTP client closed")
