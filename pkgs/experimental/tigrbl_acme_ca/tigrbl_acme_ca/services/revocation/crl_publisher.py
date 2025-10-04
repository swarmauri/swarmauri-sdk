from __future__ import annotations

from tigrbl.hook import hook_ctx

@hook_ctx(ops=("revoke_cert",), phase="POST_COMMIT")
async def _enqueue_crl_update(cls, ctx):
    # Integrate with your CRL publishing pipeline via ctx-injected queue.
    queue = ctx.get("crl_queue")
    rev = ctx.get("result")
    if queue and rev:
        try:
            await queue.enqueue({"type": "crl_update", "revocation_id": getattr(rev, "id", None)})
        except Exception:
            pass
