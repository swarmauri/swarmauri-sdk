# peagen/worker/base.py

from __future__ import annotations

import asyncio
import logging
from swarmauri_standard.loggers.Logger import Logger
import os
import socket
import uuid
from typing import Any, Awaitable, Callable, Dict, List, Optional

import httpx
from fastapi import Body, FastAPI, Request
from json.decoder import JSONDecodeError

from peagen.transport import RPCDispatcher, RPCRequest, RPCResponse

# ──────────────────────────── utils  ────────────────────────────
def get_local_ip() -> str:
    """
    Open a dummy socket to a known public host and return your own IP.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


# ──────────────────────────── WorkBase class  ────────────────────────────
class WorkerBase:
    """
    A reusable base worker that:
      • Exposes /rpc as a JSON-RPC 2.0 endpoint
      • Implements Work.start, Work.cancel
      • Has a healthcheck (/health)
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
        self.DQ_GATEWAY = gateway or os.getenv("DQ_GATEWAY", "http://localhost:8000/rpc")
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

        # ─── Shutdown state ──────────────────────────────────────────
        self._draining: bool = False
        self._task_registry: Dict[str, asyncio.Task] = {}
        self._fast_shutdown: bool = bool(int(os.getenv("DQ_FAST_SHUTDOWN", "0")))

        # ─── Handlers registry: name (str) → async function(task: Dict)→Dict ─
        self._handler_registry: Dict[str, Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]] = {}

        # ─── REGISTER built‐in RPC methods ──────────────────────────
        # 1) Work.start  →  on_work_start (async)
        @self.rpc.method("Work.start")
        async def on_work_start(task: Dict[str, Any]) -> Dict[str, Any]:
            self.log.info("Work.start received    task=%s pool=%s", task.get("id"), self.POOL)
            if self._draining:
                self.log.info("Rejecting task %s - worker draining", task.get("id"))
                return {"accepted": False}
            fut = asyncio.create_task(self._run_task_wrapper(task))
            self._task_registry[task.get("id")] = fut
            return {"accepted": True}

        # 2) Work.cancel → calls work_cancel (sync or async)
        @self.rpc.method("Work.cancel")
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
                return {"jsonrpc": "2.0", "error": {"code": -32700, "message": str(e)}, "id": body.id}
            if resp.get("error"):
                self.log.warning("%s error → %s", body.method, resp["error"])
            else:
                self.log.debug("RPC  →  %s", resp)
            return resp

        # ─── HEALTHCHECK ───────────────────────────────────────────
        @self.app.get("/health", tags=["health"])
        async def health() -> Dict[str, str]:
            return {"status": "ok"}

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
    async def _run_task_wrapper(self, task: Dict[str, Any]) -> None:
        task_id = task.get("id")
        try:
            await self._run_task(task)
        except asyncio.CancelledError:
            pass
        finally:
            self._task_registry.pop(task_id, None)

    async def _run_task(self, task: Dict[str, Any]) -> None:
        """
        Called when Work.start arrives (in on_work_start).  
        Will:
          1) Look at payload["action"]
          2) If not registered, immediately _notify failed
          3) If registered, call handler(task) → result_dict
          4) On success: _notify("success", taskId, result_dict)
             On exception: _notify("failed", taskId, {"error": ...})
        """
        task_id = task.get("id")
        payload = task.get("payload", {})
        action = payload.get("action")

        if action not in self._handler_registry:
            await self._notify("failed", task_id, {"error": f"Unsupported handler '{action}'"})
            return

        handler = self._handler_registry[action]
        # Immediately tell gateway we’re “running”
        await self._notify("running", task_id)

        try:
            result: Dict[str, Any] = await handler(task)
            await self._notify("success", task_id, result)
        except asyncio.CancelledError:
            # Task cancelled due to fast shutdown
            return
        except Exception as exc:
            await self._notify("failed", task_id, {"error": str(exc)})

    # ────────────────────────── Internal: send Work.finished ───────────────────────
    async def _notify(self, state: str, task_id: str, result: Dict[str, Any] | None = None) -> None:
        """
        Send a Work.finished (or status update) back to the gateway.
        state ∈ {"running", "success", "failed"}.
        """
        if self._client is None:
            raise RuntimeError("HTTP client not initialized")

        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "Work.finished",
            "params": {"taskId": task_id, "status": state, "result": result},
        }
        try:
            await self._client.post(self.DQ_GATEWAY, json=payload)
            self.log.info("Work.finished sent    task=%s state=%s", task_id, state)
        except Exception as exc:
            self.log.error("Failed to send Work.finished for %s: %s", task_id, exc)

    # ───────────────────────── Startup / Heartbeat / Shutdown ──────────────────────
    async def _send_rpc(self, method: str, params: Dict[str, Any]) -> None:
        """
        Helper to send any JSON-RPC call to the gateway:
          { "jsonrpc":"2.0", "id": uuid, "method": method, "params": params }
        """
        if self._client is None:
            raise RuntimeError("HTTP client not initialized")
        body = {"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": method, "params": params}
        try:
            await self._client.post(self.DQ_GATEWAY, json=body)
            self.log.debug("sent %s → %s", method, params)
        except Exception as exc:
            self.log.warning("Failed sending %s to gateway: %s", method, exc)

    async def _on_startup(self) -> None:
        """
        Called when FastAPI starts. Initialize HTTP client, register worker, start heartbeat.
        """
        self._client = httpx.AsyncClient(timeout=10)

        # ───── Worker.register ─────────────────────────────────────
        await self._send_rpc(
            "Worker.register",
            {
                "workerId": self.WORKER_ID,
                "pool": self.POOL,
                "url": self.url_self,
                "advertises": {"cpu": True},
            },
        )
        self.log.info("registered  id=%s pool=%s url=%s", self.WORKER_ID, self.POOL, self.url_self)

        # ───── Heartbeat loop ─────────────────────────────────────
        async def _heartbeat_loop() -> None:
            while True:
                await asyncio.sleep(5)
                try:
                    await self._send_rpc(
                        "Worker.heartbeat",
                        {
                            "workerId": self.WORKER_ID,
                            "pool": self.POOL,
                            "url": self.url_self,
                            "state": "draining" if self._draining else "active",
                            "metrics": {},
                        },
                    )
                    self.log.debug("heartbeat ok")
                except Exception as exc:
                    self.log.warning("heartbeat failed: %s", exc)

        asyncio.create_task(_heartbeat_loop())

    async def _on_shutdown(self) -> None:
        """
        Called when FastAPI shuts down. Close HTTP client.
        """
        self._draining = True
        requeue: List[str] = []
        if self._fast_shutdown:
            for tid, task in list(self._task_registry.items()):
                if not task.done():
                    task.cancel()
                    requeue.append(tid)
        await self._send_rpc(
            "Worker.shutdown",
            {
                "workerId": self.WORKER_ID,
                "fast": self._fast_shutdown,
                "requeue": requeue,
            },
        )
        if self._task_registry:
            await asyncio.gather(*self._task_registry.values(), return_exceptions=True)
        if self._client:
            await self._client.aclose()
            self.log.info("HTTP client closed")
