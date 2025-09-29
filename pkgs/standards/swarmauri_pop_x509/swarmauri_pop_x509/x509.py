from __future__ import annotations

from typing import Mapping

from swarmauri_core.pop import (
    BindType,
    CnfBinding,
    Feature,
    PoPBindingError,
    PoPParseError,
    PoPKind,
)
from swarmauri_base.pop import PopVerifierBase, RequestContext, sha256_b64u


class X509PoPVerifier(PopVerifierBase):
    """Verifier for TLS client-certificate proof-of-possession."""

    def __init__(self) -> None:
        super().__init__(
            kind=PoPKind.X509,
            header_name="",  # No detached header; proof is in the TLS handshake
            features=Feature.MTLS,
            algorithms=("tls13-handshake",),
        )

    def _extract_proof(self, req):  # type: ignore[override]
        return ""

    async def _verify_core(
        self,
        proof: str,
        context: RequestContext,
        cnf: CnfBinding,
        *,
        replay,
        keys,
        extras: Mapping[str, object],
    ) -> None:
        self._enforce_bind_type(cnf, context.policy, expected=BindType.X5T_S256)

        cert_bytes = extras.get("peer_cert_der")
        if cert_bytes is None:
            raise PoPParseError("peer_cert_der extra is required for X.509 PoP")
        if not isinstance(cert_bytes, (bytes, bytearray)):
            raise PoPParseError("peer_cert_der must be bytes")

        thumb = sha256_b64u(bytes(cert_bytes))
        if thumb != cnf.value_b64u:
            raise PoPBindingError("mTLS certificate thumbprint does not match cnf")
