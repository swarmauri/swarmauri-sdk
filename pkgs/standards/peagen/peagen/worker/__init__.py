# peagen/worker.py

import asyncio
from fastapi import Request
from typing import Any, Dict

from peagen.worker.base import WorkerBase
from peagen.handlers.doe_handler import doe_handler
from peagen.handlers.fetch_handler import fetch_handler
from peagen.handlers.eval_handler import eval_handler
from peagen.handlers.process_handler import process_handler
from peagen.handlers.sort_handler import sort_handler

# ----------------------------------------------------------------------------
# Subclass WorkerBase (optional) so you can override or extend methods if needed.
# If you don’t need to override anything, you can also just instantiate WorkerBase
# directly in a script (no subclass). But here’s how to subclass:
# ----------------------------------------------------------------------------
class PeagenWorker(WorkerBase):
    def __init__(self):
        # Let WorkerBase pick up ENV or defaults for pool/gateway/host/port
        super().__init__()
        # Register all handlers you want this worker to support:
        self.register_handler("doe", doe_handler)
        self.register_handler("eval", eval_handler)
        self.register_handler("fetch", fetch_handler)
        self.register_handler("process", process_handler)
        self.register_handler("sort", sort_handler)
        # In the future, you might also do:
        #   from peagen.handlers.render_handler import render_handler
        #   self.register_handler("render", render_handler)
        # etc.

    # If you ever want to customize Work.cancel behavior, override:
    # async def work_cancel(self, taskId: str) -> Dict[str,Any]:
    #     ...
    #     return {"ok": True}


# ──────────────────────────────────────────────────────────────────────────────
# Instantiate the worker and expose FastAPI app as “app” so Uvicorn/Gunicorn can run it
# ──────────────────────────────────────────────────────────────────────────────
worker = PeagenWorker()
app = worker.app


# (Optionally) if you need to add more FastAPI routes, you can do so here, e.g.:
# @app.get("/some-other-endpoint")
# async def custom_endpoint() -> Dict[str, Any]:
#     return {"message": "hello from PeagenWorker"}
