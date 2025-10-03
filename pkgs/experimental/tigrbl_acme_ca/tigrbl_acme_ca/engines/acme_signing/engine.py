from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from tigrbl_acme_ca.libs.sw_cert_service import CertService, IssueResult
from tigrbl_acme_ca.key_mgmt.ca_key_loader import CaKeyLoader


@dataclass
class AcmeSigningEngine:
    """Thin engine that issues end-entity certificates for ACME Orders.

    It delegates to a CertService (which may use cryptography or a backend)
    and a CaKeyLoader (which provides the issuing CA key material or adapter).
    """
    cert_service: CertService
    key_loader: CaKeyLoader
    default_validity_days: int = 90

    @classmethod
    def from_config(cls, config: dict) -> "AcmeSigningEngine":
        service = CertService.from_config(config or {})
        loader = CaKeyLoader.from_config(config or {})
        return cls(cert_service=service, key_loader=loader,
                   default_validity_days=int((config or {}).get("acme.validity_days", 90)))

    async def issue_certificate(self, *, csr_der: bytes, sans: List[str]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        not_before = now
        not_after = now + timedelta(days=self.default_validity_days)

        issuer = await self.key_loader.load_issuer_key()  # may be a cryptography key or adapter
        issued: IssueResult = await self.cert_service.issue_certificate(
            csr_der=csr_der,
            sans=sans,
            issuer_key=issuer,
            not_before=not_before,
            not_after=not_after,
        )
        return {
            "pem": issued.pem,
            "serial_hex": issued.serial_hex,
            "not_before": issued.not_before,
            "not_after": issued.not_after,
        }
