from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException

# Optional cryptography imports; if unavailable, fall back to cached bytes
try:
    from cryptography import x509
    from cryptography.x509 import ocsp
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, ec
except Exception:  # pragma: no cover
    x509 = None
    ocsp = None
    hashes = None
    serialization = None
    rsa = None
    ec = None


@dataclass
class OcspCacheItem:
    certificate_id: str
    response_der: bytes
    updated_at: datetime


def _h(ctx, name: str):
    handlers = ctx.get("handlers") or {}
    fn = handlers.get(name)
    if not fn:
        raise HTTPException(status_code=500, detail=f"handler_unavailable:{name}")
    return fn


def _id(obj):
    return obj.get("id") if isinstance(obj, dict) else getattr(obj, "id", None)


def _field(obj, name: str):
    return obj.get(name) if isinstance(obj, dict) else getattr(obj, name, None)


class InMemoryOcspResponder:
    """A minimal OCSP responder that can refresh per-certificate responses.

    If 'cryptography' is available and you provide issuer cert/key in ctx,
    it builds a BasicOCSPResponse. Otherwise, it returns/updates a cached
    byte payload with a simple JSON structure (not suitable for production OCSP).
    """

    def __init__(self):
        self._cache: dict[str, OcspCacheItem] = {}

    async def refresh(self, *, certificate_id: str, ctx: dict | None = None) -> bytes:
        ctx = ctx or {}
        if x509 is None or ocsp is None:
            # Fallback: store a simple JSON payload as bytes
            import json

            payload = {
                "certificate_id": certificate_id,
                "status": "unknown",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            data = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode(
                "utf-8"
            )
            self._cache[certificate_id] = OcspCacheItem(
                certificate_id=certificate_id,
                response_der=data,
                updated_at=datetime.now(timezone.utc),
            )
            return data

        # With cryptography: build a "good" OCSP response by default.
        # Use handlers instead of direct DB.
        db = ctx.get("db")
        if db is None:
            # Can't load certs without DB in this simple implementation.
            return b""

        # Load leaf certificate PEM from DB.
        from tigrbl_acme_ca.tables.certificates import Certificate

        read_by_id = _h(ctx, "table.read.by_id")
        cert_row = await read_by_id(table=Certificate, id=certificate_id)
        if not cert_row:
            return b""
        cert_pem = (
            cert_row.get("pem")
            if isinstance(cert_row, dict)
            else getattr(cert_row, "pem", None)
        )
        if not cert_pem:
            return b""
        try:
            cert = x509.load_pem_x509_certificate(cert_pem.encode("utf-8"))
        except Exception:
            return b""

        # Issuer cert and key must be provided in ctx
        issuer_pem = ctx.get("ocsp_issuer_cert_pem")
        issuer_key = ctx.get("ocsp_responder_key")
        if not issuer_pem or issuer_key is None:
            # If not provided, return cached (or empty) to avoid failure
            item = self._cache.get(certificate_id)
            return item.response_der if item else b""
        try:
            issuer = x509.load_pem_x509_certificate(issuer_pem.encode("utf-8"))
        except Exception:
            return b""

        # cryptography's API requires building through OCSPResponseBuilder on the entry.
        # Workaround: use ocsp.OCSPResponseBuilder.add_response directly on a fresh builder.
        builder = ocsp.OCSPResponseBuilder()
        builder = builder.add_response(
            cert=cert,
            issuer=issuer,
            algorithm=hashes.SHA256(),
            cert_status=ocsp.OCSPCertStatus.GOOD,
            this_update=datetime.now(timezone.utc),
            next_update=datetime.now(timezone.utc) + timedelta(hours=4),
            revocation_time=None,
            revocation_reason=None,
        )
        try:
            response = builder.responder_id(
                ocsp.OCSPResponderEncoding.HASH, issuer.subject
            ).sign(
                private_key=issuer_key,
                algorithm=hashes.SHA256(),
            )
            data = response.public_bytes(serialization.Encoding.DER)
        except Exception:
            # On failure, return empty bytes to avoid poisoning cache
            return b""

        item = OcspCacheItem(
            certificate_id=certificate_id,
            response_der=data,
            updated_at=datetime.now(timezone.utc),
        )
        self._cache[certificate_id] = item
        return data

    async def get_cached(self, certificate_id: str) -> bytes | None:
        item = self._cache.get(certificate_id)
        return item.response_der if item else None
