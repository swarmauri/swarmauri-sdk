# peagen/worker.py

from peagen.worker.base import WorkerBase
from peagen.handlers.doe_handler import doe_handler
from peagen.handlers.doe_process_handler import doe_process_handler
from peagen.handlers.fetch_handler import fetch_handler
from peagen.handlers.eval_handler import eval_handler
from peagen.handlers.process_handler import process_handler
from peagen.handlers.sort_handler import sort_handler
from peagen.handlers.mutate_handler import mutate_handler
from peagen.handlers.evolve_handler import evolve_handler

# from peagen.handlers.login_handler import login_handler
from peagen.handlers.keys_handler import keys_handler
from peagen.handlers.secrets_handler import secrets_handler


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
        self.register_handler("doe_process", doe_process_handler)
        self.register_handler("eval", eval_handler)
        self.register_handler("fetch", fetch_handler)
        self.register_handler("process", process_handler)
        self.register_handler("sort", sort_handler)
        self.register_handler("mutate", mutate_handler)
        self.register_handler("evolve", evolve_handler)
        # self.register_handler("login", login_handler)
        self.register_handler("keys", keys_handler)
        self.register_handler("secrets", secrets_handler)
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
