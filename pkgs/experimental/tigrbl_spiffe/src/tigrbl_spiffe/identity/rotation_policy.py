from __future__ import annotations

from typing import Any, Dict, Tuple

class RotationPolicy:
    """Computes the next material for an SVID.

    Pulls from a remote Workload API via ctx extras when available.
    """

    async def rotate(self, *, current: Any, ctx: dict[str, Any]) -> dict:
        adapter = ctx.get("spiffe_adapter")
        cfg = ctx.get("spiffe_config")
        if adapter and cfg:
            # Prefer remote fetch for fresh SVIDs
            tx = await adapter.for_endpoint(cfg.workload_endpoint)
            kind = getattr(current, "kind", "x509")
            if kind == "x509" and tx.kind == "uds":
                from pyspiffe.workloadapi.default_workload_api_client import DefaultWorkloadApiClient
                client = DefaultWorkloadApiClient(socket_path=tx.uds_path)
                try:
                    svid = client.fetch_x509_svid()
                    chain_der = b"".join(c.public_bytes() for c in svid.cert_chain)  # type: ignore[attr-defined]
                    exp = int(svid.expires_at.timestamp())
                    return {
                        "material": chain_der,
                        "not_before": exp - 3600,
                        "not_after": exp,
                        "audiences": tuple(getattr(current, "audiences", ()) or ()),
                    }
                finally:
                    client.close()

            if kind == "jwt" and tx.http is not None:
                data = (await tx.http.post("/workload/jwtsvid", json={"aud": list(getattr(current, "audiences", ())) })).json()
                return {
                    "material": data["jwt"].encode("utf-8"),
                    "not_before": data.get("nbf", 0),
                    "not_after": data.get("exp", 0),
                    "audiences": tuple(data.get("aud", [])),
                }

            if kind == "cwt" and tx.http is not None:
                data = (await tx.http.post("/workload/cwtsvid", json={"aud": list(getattr(current, "audiences", ())) })).json()
                return {
                    "material": data["cwt"].encode("utf-8"),
                    "not_before": data.get("nbf", 0),
                    "not_after": data.get("exp", 0),
                    "audiences": tuple(data.get("aud", [])),
                }

        # Fallback: return current material (no change). A real policy might fail closed.
        return {
            "material": getattr(current, "material", b""),
            "not_before": getattr(current, "not_before", 0),
            "not_after": getattr(current, "not_after", 0),
            "audiences": tuple(getattr(current, "audiences", ()) or ()),
        }
