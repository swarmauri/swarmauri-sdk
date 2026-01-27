from __future__ import annotations

from typing import Tuple

import httpx

from tigrbl import engine_ctx, op_ctx
from tigrbl.orm.tables import Base
from tigrbl.specs import acol, S, F, IO
from tigrbl.types import String, Integer, LargeBinary, HTTPException

from ..workload_client import WorkloadClientError, fetch_remote_svid


@engine_ctx(kind="sqlite", async_=True, mode="memory")
class Workload(Base):
    __abstract__ = True
    __tablename__ = "spiffe_workload"
    __resource__ = "workload"

    # Shape hints for response schemas (not persisted)
    spiffe_id = acol(
        storage=S(type_=String(255), nullable=True),
        field=F(py_type=str),
        io=IO(out_verbs=("read",)),
    )
    kind = acol(
        storage=S(type_=String(10), nullable=True),
        field=F(py_type=str),
        io=IO(out_verbs=("read",)),
    )
    not_before = acol(
        storage=S(type_=Integer, nullable=True),
        field=F(py_type=int),
        io=IO(out_verbs=("read",)),
    )
    not_after = acol(
        storage=S(type_=Integer, nullable=True),
        field=F(py_type=int),
        io=IO(out_verbs=("read",)),
    )
    audiences = acol(
        storage=S(type_=String(255), nullable=True),
        field=F(py_type=Tuple[str, ...]),
        io=IO(out_verbs=("read",)),
    )
    material = acol(
        storage=S(type_=LargeBinary, nullable=True),
        field=F(py_type=bytes),
        io=IO(out_verbs=("read",)),
    )

    @op_ctx(alias="read", persist="skip")
    async def _remote_read(cls, ctx):
        payload = ctx.get("payload") or {}
        kind = payload.get("kind") or "x509"
        aud = payload.get("aud") or ()
        adapter = ctx.get("spiffe_adapter")
        cfg = ctx.get("spiffe_config")
        if adapter is None or cfg is None:
            raise HTTPException(
                status_code=500,
                detail="SPIFFE adapter/config missing for workload read",
            )
        tx = await adapter.for_endpoint(cfg.workload_endpoint)
        try:
            return await fetch_remote_svid(tx, kind=kind, audiences=tuple(aud))
        except WorkloadClientError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=502, detail="Workload endpoint request failed"
            ) from exc
