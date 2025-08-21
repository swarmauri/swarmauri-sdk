from __future__ import annotations

from typing import Iterable, Mapping, Optional, Sequence, Dict, Any, Literal

from swarmauri_core.certs.ICertService import ICertService
from swarmauri_base.certs.CertServiceBase import CertServiceBase
from swarmauri_core.crypto.types import KeyRef


class CompositeCertService(CertServiceBase):
    """
    Router that delegates ICertService operations to one of several providers.
    Useful when you have multiple backends (local CA, ACME, PKCS#11, Vault, etc.)
    and want one facade for apps.

    Compliant with RFC 5280 and RFC 2986.

    Routing strategy:
      - For create_csr: first provider that advertises "csr" in supports().
      - For create_self_signed: first provider with "self_signed".
      - For sign_cert: provider chosen by opts["backend"] if provided,
        otherwise first with "sign_from_csr".
      - For verify_cert/parse_cert: first provider with "verify"/"parse".

    Callers can override routing by passing opts={"backend":"ProviderType"}.
    """

    type: Literal["CompositeCertService"] = "CompositeCertService"

    def __init__(self, providers: Sequence[ICertService]) -> None:
        super().__init__()
        if not providers:
            raise ValueError("CompositeCertService requires at least one provider")
        self._providers: Dict[str, ICertService] = {p.type: p for p in providers}

    def supports(self) -> Mapping[str, Iterable[str]]:
        # Aggregate union of all providers
        agg: Dict[str, set[str]] = {}
        for p in self._providers.values():
            caps = p.supports()
            for k, v in caps.items():
                agg.setdefault(k, set()).update(v)
        return {k: tuple(v) for k, v in agg.items()}

    # ------------------ routing helpers ------------------

    def _pick(
        self, feature: str, opts: Optional[Dict[str, Any]] = None
    ) -> ICertService:
        # Explicit backend request wins
        if opts and "backend" in opts:
            backend = opts["backend"]
            if backend in self._providers:
                return self._providers[backend]
            raise ValueError(f"No such backend registered: {backend}")

        # Otherwise, pick first provider that advertises the feature
        for p in self._providers.values():
            if feature in p.supports().get("features", ()):
                return p
        raise RuntimeError(f"No provider supports feature={feature!r}")

    # ------------------ delegated methods ------------------

    async def create_csr(self, key: KeyRef, subject, **kw) -> bytes:
        return await self._pick("csr", kw.get("opts")).create_csr(key, subject, **kw)

    async def create_self_signed(self, key: KeyRef, subject, **kw) -> bytes:
        return await self._pick("self_signed", kw.get("opts")).create_self_signed(
            key, subject, **kw
        )

    async def sign_cert(self, csr: bytes, ca_key: KeyRef, **kw) -> bytes:
        return await self._pick("sign_from_csr", kw.get("opts")).sign_cert(
            csr, ca_key, **kw
        )

    async def verify_cert(self, cert: bytes, **kw) -> Dict[str, Any]:
        return await self._pick("verify", kw.get("opts")).verify_cert(cert, **kw)

    async def parse_cert(self, cert: bytes, **kw) -> Dict[str, Any]:
        return await self._pick("parse", kw.get("opts")).parse_cert(cert, **kw)
