from __future__ import annotations

from typing import Optional, Tuple

from tigrbl import engine_ctx, hook_ctx, op_ctx
import tigrbl.core as core
from tigrbl.orm.tables import Base
from tigrbl.specs import acol, S, F, IO
from tigrbl.types import String, Integer, JSON, HTTPException


@engine_ctx(kind="sqlite", async_=True, mode="memory")
class Registrar(Base):
    __tablename__ = "spiffe_registrar"
    __resource__ = "registrar"

    entry_id = acol(
        storage=S(type_=String(255), primary_key=True),
        field=F(py_type=str),
        io=IO(out_verbs=("read", "list")),
    )

    spiffe_id = acol(
        storage=S(type_=String(255), nullable=False, index=True),
        field=F(py_type=str, required_in=("create",)),
        io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list"), filter_ops=("eq",)),
    )

    parent_id = acol(
        storage=S(type_=String(255), nullable=True, index=True),
        field=F(py_type=str),
        io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list"), filter_ops=("eq",)),
    )

    selectors = acol(
        storage=S(type_=JSON, nullable=True),
        field=F(py_type=Tuple[Tuple[str, str], ...]),
        io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")),
    )

    ttl_s = acol(
        storage=S(type_=Integer, nullable=False, default=0),
        field=F(py_type=int),
        io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")),
    )

    @hook_ctx(ops=("create","merge","replace"), phase="PRE_HANDLER")
    async def _validate_entry(cls, ctx):
        payload = ctx.get("payload") or {}
        data = payload.get("data") or {}
        sels = data.get("selectors") or ()
        if sels and not all(isinstance(x, (list, tuple)) and len(x) == 2 for x in sels):
            raise HTTPException(status_code=400, detail="selectors must be list of [type, value]")

    @op_ctx(alias="read")
    async def _read_override(cls, ctx):
        payload = ctx.get("payload") or {}
        if not payload.get("remote"):
            ident = (ctx.get("path_params") or {}).get("id")
            db = ctx.get("db")
            if ident is None:
                return await core.list(cls, db=db, filters=(payload.get("filters") or {}), sort=payload.get("sort"))
            return await core.read(cls, ident, db=db)

        adapter = ctx.get("spiffe_adapter")
        cfg = ctx.get("spiffe_config")
        if adapter is None or cfg is None:
            raise HTTPException(status_code=500, detail="SPIFFE adapter/config missing for remote read")
        tx = await adapter.for_endpoint(cfg.server_endpoint)
        if tx.kind in {"uds","grpc"}:
            raise HTTPException(status_code=501, detail="gRPC path not implemented")
        ident = (ctx.get("path_params") or {}).get("id")
        if ident:
            data = (await tx.http.get(f"/server/registration/entries/{ident}")).json()
            return data
        data = (await tx.http.get("/server/registration/entries")).json()
        return data.get("items", [])
