from __future__ import annotations

from tigrbl import engine_ctx, hook_ctx
from tigrbl.orm.tables import Base
from tigrbl.specs import acol, S, F, IO
from tigrbl.types import String, Integer, JSON, Text, HTTPException


@engine_ctx(kind="sqlite", async_=True, mode="memory")
class Bundle(Base):
    __tablename__ = "spiffe_bundle"
    __resource__ = "bundle"

    trust_domain = acol(
        storage=S(type_=String(255), primary_key=True),
        field=F(py_type=str),
        io=IO(out_verbs=("read","list")),
    )

    x509_authorities_pem = acol(
        storage=S(type_=Text, nullable=True),
        field=F(py_type=str),
        io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")),
    )

    jwt_jwks = acol(
        storage=S(type_=JSON, nullable=True),
        field=F(py_type=dict),
        io=IO(in_verbs=("create","update","replace","merge"), out_verbs=("read","list")),
    )

    updated_at = acol(
        storage=S(type_=Integer, nullable=False, default=0),
        field=F(py_type=int),
        io=IO(out_verbs=("read","list")),
    )

    @hook_ctx(ops=("create","merge","replace"), phase="PRE_HANDLER")
    async def _validate_bundle(cls, ctx):
        payload = ctx.get("payload") or {}
        data = payload.get("data") or {}
        pem = data.get("x509_authorities_pem")
        jwks = data.get("jwt_jwks")
        if not pem and not jwks:
            raise HTTPException(status_code=400, detail="bundle requires x509_authorities_pem or jwt_jwks")
