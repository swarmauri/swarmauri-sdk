from __future__ import annotations

from typing import Any

import httpx

from ..workload_client import WorkloadClientError, fetch_remote_svid


class RotationPolicy:
    """Computes the next material for an SVID.

    Pulls from a remote Workload API via ctx extras when available.
    """

    async def rotate(self, *, current: Any, ctx: dict[str, Any]) -> dict:
        adapter = ctx.get("spiffe_adapter")
        cfg = ctx.get("spiffe_config")
        if adapter and cfg:
            tx = await adapter.for_endpoint(cfg.workload_endpoint)
            kind = getattr(current, "kind", "x509")
            audiences = tuple(getattr(current, "audiences", ()) or ())
            try:
                remote = await fetch_remote_svid(tx, kind=kind, audiences=audiences)
            except (WorkloadClientError, httpx.HTTPError):
                remote = None
            if remote:
                return {
                    "material": remote["material"],
                    "not_before": remote["not_before"],
                    "not_after": remote["not_after"],
                    "audiences": tuple(remote.get("audiences", audiences)),
                }

        # Fallback: return current material (no change). A real policy might fail closed.
        return {
            "material": getattr(current, "material", b""),
            "not_before": getattr(current, "not_before", 0),
            "not_after": getattr(current, "not_after", 0),
            "audiences": tuple(getattr(current, "audiences", ()) or ()),
        }
