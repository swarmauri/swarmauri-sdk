from __future__ import annotations

from enum import Enum
from typing import Optional, Tuple

from tigrbl import engine_ctx, op_ctx, hook_ctx
import tigrbl.core as core
from tigrbl.orm.tables import Base
from tigrbl.specs import acol, vcol, S, F, IO
from tigrbl.types import (
    Integer,
    String,
    LargeBinary,
    JSON,
    SAEnum,
    HTTPException,
)

try:
    from ..types import SvidKind as _SvidKind
except Exception:  # fallback if types module isn't present yet
    class _SvidKind(str, Enum):
        x509 = "x509"
        jwt = "jwt"
        cwt = "cwt"


class SvidStatus(str, Enum):
    active = "active"
    staged = "staged"
    retired = "retired"


@engine_ctx(kind="sqlite", async_=True, mode="memory")
class Svid(Base):
    __tablename__ = "spiffe_svid"
    __resource__ = "svid"

    # Primary key: SPIFFE ID
    spiffe_id = acol(
        storage=S(type_=String(255), primary_key=True, index=True),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("read", "list"), filter_ops=("eq",)),
    )

    # Discriminator: kind of SVID
    kind = acol(
        storage=S(type_=SAEnum(_SvidKind, name="svid_kind"), nullable=False),
        field=F(py_type=_SvidKind),
        io=IO(in_verbs=("create", "update", "replace", "merge"), out_verbs=("read", "list"), filter_ops=("eq",)),
    )

    # Version + lifecycle
    version = acol(
        storage=S(type_=Integer, nullable=False, default=1),
        field=F(py_type=int),
        io=IO(in_verbs=("update", "replace", "merge"), out_verbs=("read", "list"), sortable=True),
    )

    status = acol(
        storage=S(type_=SAEnum(SvidStatus, name="svid_status"), nullable=False, default=SvidStatus.active),
        field=F(py_type=SvidStatus),
        io=IO(in_verbs=("update", "replace", "merge"), out_verbs=("read", "list"), filter_ops=("eq",)),
    )

    # Validity window (epoch seconds)
    not_before = acol(
        storage=S(type_=Integer, nullable=False),
        field=F(py_type=int, required_in=("create",)),
        io=IO(in_verbs=("create", "update", "replace", "merge"), out_verbs=("read", "list"), sortable=True, filter_ops=("ge","le","gt","lt","eq")),
    )

    not_after = acol(
        storage=S(type_=Integer, nullable=False),
        field=F(py_type=int, required_in=("create",)),
        io=IO(in_verbs=("create", "update", "replace", "merge"), out_verbs=("read", "list"), sortable=True, filter_ops=("ge","le","gt","lt","eq")),
    )

    # Audiences (JWT/CWT) or x509 EKUs/URI SANs mapping if needed
    audiences = acol(
        storage=S(type_=JSON, nullable=True),
        field=F(py_type=Tuple[str, ...]),
        io=IO(in_verbs=("create", "update", "replace", "merge"), out_verbs=("read", "list")),
    )

    # Material: DER chain for x509; UTF-8 token for JWT/CWT. Store as bytes to keep single storage type.
    material = acol(
        storage=S(type_=LargeBinary, nullable=False),
        field=F(py_type=bytes),
        io=IO(in_verbs=("create", "update", "replace", "merge"), out_verbs=("read",)),
    )

    # Reference to bundle (trust domain)
    bundle_id = acol(
        storage=S(type_=String(255), nullable=True, index=True),
        field=F(py_type=str),
        io=IO(in_verbs=("create", "update", "replace", "merge"), out_verbs=("read", "list"), filter_ops=("eq",)),
    )

    # Expose convenience views
    token: Optional[str] = vcol(
        io=IO(out_verbs=("read",)),
        read_producer=lambda obj, ctx: obj.material.decode("utf-8") if getattr(obj, "kind", "jwt") in ("jwt", "cwt") else None,
    )

    chain_der_hex: Optional[str] = vcol(
        io=IO(out_verbs=("read",)),
        read_producer=lambda obj, ctx: obj.material.hex() if getattr(obj, "kind", "x509") == "x509" else None,
    )

    @hook_ctx(ops=("create", "merge", "replace"), phase="PRE_HANDLER")
    async def _validate_svid(cls, ctx):
        """Validate SVID material against declared kind and bundle.

        This is a hook (not middleware) to keep validation close to persistence.

        No kernel atoms are used; no emits.

        """
        payload = ctx.get("payload") or {}
        data = payload.get("data") or {}
        kind = data.get("kind")
        material = data.get("material")
        if material is None or kind is None:
            return  # Let core validation handle missing fields

        # Accept bytes or base64-encoded string
        if isinstance(material, str):
            try:
                material_bytes = material.encode("utf-8")
            except Exception:
                raise HTTPException(status_code=400, detail="material must be bytes or utf-8 string")
        else:
            material_bytes = material

        validator = ctx.get("svid_validator")
        if validator is None:
            # Optional: allow write without strict validation if not wired
            return

        # Delegate to provided validator; must raise HTTPException on failure
        await validator.validate(kind=kind, material=material_bytes, bundle_id=data.get("bundle_id"), ctx=ctx)

    @op_ctx(alias="rotate", target="custom", arity="member", persist="write")
    async def rotate(cls, ctx):
        """Rotate the SVID in-place (single-row SoT): version++, material, validity.

        Uses a rotation policy provided in ctx as `rotation_policy`.

        """
        db = ctx.get("db")
        if db is None:
            raise HTTPException(status_code=500, detail="DB session missing")

        ident = (ctx.get("path_params") or {}).get("id") or (ctx.get("payload") or {}).get("id")
        if ident is None:
            raise HTTPException(status_code=400, detail="Missing item id for rotation")

        # Load current object
        obj = await core.read(cls, ident, db=db)
        if obj is None:
            raise HTTPException(status_code=404, detail="SVID not found")

        policy = ctx.get("rotation_policy")
        if policy is None:
            raise HTTPException(status_code=500, detail="Rotation policy missing")

        # Compute next SVID material via policy (returns dict fields to merge)
        # Expected keys: material (bytes), not_before(int), not_after(int), audiences(tuple[str,...]) optional
        patch = await policy.rotate(current=obj, ctx=ctx)
        if not isinstance(patch, dict) or b"" is None:
            raise HTTPException(status_code=500, detail="Invalid rotation policy result")

        # Merge in-place (version++, status->active)
        data = {
            "version": int(getattr(obj, "version", 1)) + 1,
            "material": patch.get("material", getattr(obj, "material")),
            "not_before": patch.get("not_before", getattr(obj, "not_before")),
            "not_after": patch.get("not_after", getattr(obj, "not_after")),
            "audiences": tuple(patch.get("audiences", getattr(obj, "audiences", ()) or ())),
            "status": SvidStatus.active,
        }
        result = await core.merge(cls, ident, data=data, db=db)
        return result

    @op_ctx(alias="read")
    async def _read_override(cls, ctx):
        """Optionally delegate reads to a remote Workload API when requested.

        Pass `{ "remote": true, "kind": ..., "aud": [...] }` in payload to trigger remote fetch.

        Otherwise, fall back to core.read semantics.

        """
        payload = ctx.get("payload") or {}
        if not payload.get("remote") :
            # Default: core read/list behavior
            ident = (ctx.get("path_params") or {}).get("id")
            db = ctx.get("db")
            if ident is None:
                # collection read
                return await core.list(cls, db=db, filters=(payload.get("filters") or {}), sort=payload.get("sort"))
            return await core.read(cls, ident, db=db)

        # Remote delegation (no DB writes) via adapter provided by middleware
        adapter = ctx.get("spiffe_adapter")
        cfg = ctx.get("spiffe_config")
        if adapter is None or cfg is None:
            raise HTTPException(status_code=500, detail="SPIFFE adapter/config missing for remote read")

        kind = payload.get("kind") or "x509"
        aud = payload.get("aud") or ()
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
                    "version": 1,
                    "status": "active",
                    "not_before": int(svid.expires_at.timestamp()) - 3600,  # conservative
                    "not_after": int(svid.expires_at.timestamp()),
                    "audiences": tuple(aud),
                    "material": chain_der,
                }
            finally:
                client.close()
        # HTTP/HTTPS path or other kinds
        if kind == "jwt":
            resp = await tx.http.post("/workload/jwtsvid", json={"aud": list(aud)})
            data = resp.json()
            return {
                "spiffe_id": data["spiffe_id"],
                "kind": "jwt",
                "version": 1,
                "status": "active",
                "not_before": data.get("nbf", 0),
                "not_after": data.get("exp", 0),
                "audiences": tuple(data.get("aud", [])),
                "material": data["jwt"].encode("utf-8"),
                "bundle_id": data.get("bundle_id"),
            }
        if kind == "cwt":
            resp = await tx.http.post("/workload/cwtsvid", json={"aud": list(aud)})
            data = resp.json()
            return {
                "spiffe_id": data["spiffe_id"],
                "kind": "cwt",
                "version": 1,
                "status": "active",
                "not_before": data.get("nbf", 0),
                "not_after": data.get("exp", 0),
                "audiences": tuple(data.get("aud", [])),
                "material": data["cwt"].encode("utf-8"),
                "bundle_id": data.get("bundle_id"),
            }
        raise HTTPException(status_code=400, detail=f"Unsupported kind for remote read: {kind}")
