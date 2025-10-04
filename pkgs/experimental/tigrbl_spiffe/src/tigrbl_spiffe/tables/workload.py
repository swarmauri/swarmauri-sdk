from __future__ import annotations

from typing import Tuple

from tigrbl import engine_ctx, op_ctx
from tigrbl.orm.tables import Base
from tigrbl.specs import acol, S, F, IO
from tigrbl.types import String, Integer, LargeBinary, HTTPException


@engine_ctx(kind="sqlite", async_=True, mode="memory")
class Workload(Base):
    __abstract__ = True
    __tablename__ = "spiffe_workload"
    __resource__ = "workload"

    # Shape hints for response schemas (not persisted)
    spiffe_id = acol(storage=S(type_=String(255), nullable=True), field=F(py_type=str), io=IO(out_verbs=("read",)))
    kind = acol(storage=S(type_=String(10), nullable=True), field=F(py_type=str), io=IO(out_verbs=("read",)))
    not_before = acol(storage=S(type_=Integer, nullable=True), field=F(py_type=int), io=IO(out_verbs=("read",)))
    not_after = acol(storage=S(type_=Integer, nullable=True), field=F(py_type=int), io=IO(out_verbs=("read",)))
    audiences = acol(storage=S(type_=String(255), nullable=True), field=F(py_type=Tuple[str, ...]), io=IO(out_verbs=("read",)))
    material = acol(storage=S(type_=LargeBinary, nullable=True), field=F(py_type=bytes), io=IO(out_verbs=("read",)))

    @op_ctx(alias="read", persist="skip")
    async def _remote_read(cls, ctx):
        payload = ctx.get("payload") or {}
        kind = payload.get("kind") or "x509"
        aud = payload.get("aud") or ()
        adapter = ctx.get("spiffe_adapter")
        cfg = ctx.get("spiffe_config")
        if adapter is None or cfg is None:
            raise HTTPException(status_code=500, detail="SPIFFE adapter/config missing for workload read")
        tx = await adapter.for_endpoint(cfg.workload_endpoint)

        if kind == "x509" and tx.kind == "uds":
            from pyspiffe.workloadapi.default_workload_api_client import DefaultWorkloadApiClient
            client = DefaultWorkloadApiClient(socket_path=tx.uds_path)
            try:
                svid = client.fetch_x509_svid()
                chain_der = b"".join(c.public_bytes() for c in svid.cert_chain)  # type: ignore[attr-defined]
                return {
                    "spiffe_id": str(svid.spiffe_id()),
                    "kind": "x509",
                    "not_before": int(svid.expires_at.timestamp()) - 3600,
                    "not_after": int(svid.expires_at.timestamp()),
                    "audiences": tuple(aud),
                    "material": chain_der,
                }
            finally:
                client.close()

        if kind == "jwt":
            data = (await tx.http.post("/workload/jwtsvid", json={"aud": list(aud)})).json()
            return {
                "spiffe_id": data["spiffe_id"],
                "kind": "jwt",
                "not_before": data.get("nbf", 0),
                "not_after": data.get("exp", 0),
                "audiences": tuple(data.get("aud", [])),
                "material": data["jwt"].encode("utf-8"),
                "bundle_id": data.get("bundle_id"),
            }

        if kind == "cwt":
            data = (await tx.http.post("/workload/cwtsvid", json={"aud": list(aud)})).json()
            return {
                "spiffe_id": data["spiffe_id"],
                "kind": "cwt",
                "not_before": data.get("nbf", 0),
                "not_after": data.get("exp", 0),
                "audiences": tuple(data.get("aud", [])),
                "material": data["cwt"].encode("utf-8"),
                "bundle_id": data.get("bundle_id"),
            }

        raise HTTPException(status_code=400, detail=f"Unsupported kind: {kind}")
