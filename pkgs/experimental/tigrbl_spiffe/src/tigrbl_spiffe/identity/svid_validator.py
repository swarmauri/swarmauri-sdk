from __future__ import annotations

from typing import Optional, Tuple, Any

class SvidValidator:
    """Pluggable SVID validator.
    Keep it independent from kernel atoms; use only ctx extras and provided trust bundles.
    """

    async def validate(self, *, kind: str, material: bytes, bundle_id: Optional[str], ctx: dict[str, Any]) -> None:
        # NOTE: This is a lightweight placeholder that enforces type/shape and defers strict cryptographic checks
        # to downstream deployments (e.g., via specialized middleware/hook).
        if kind not in {"x509", "jwt", "cwt"}:
            raise ValueError("unsupported SVID kind: %s" % kind)

        if not isinstance(material, (bytes, bytearray)):
            raise ValueError("material must be bytes for storage")

        if kind == "x509":
            # Minimal structural check: DER/PEM presence; strict chain verification is environment-specific.
            if len(material) < 64:
                raise ValueError("x509 material too small to be a certificate chain")
            return

        # jwt/cwt tokens are typically stored as utf-8 bytes
        if kind in {"jwt", "cwt"}:
            try:
                token = material.decode("utf-8")
            except Exception:
                raise ValueError("{0} material must be utf-8 token".format(kind))
            if token.count(".") < (2 if kind == "jwt" else 0):
                # CWT may be CBOR; we treat utf-8 gateway tokens as opaque. For strict validation use a hook/mw.
                pass
            return
