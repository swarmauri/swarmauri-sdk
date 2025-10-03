from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List

from tigrbl_acme_ca.engines.acme_signing.engine import AcmeSigningEngine

@dataclass
class AcmeSigningSession:
    """Optional per-request session wrapper around the engine."""
    engine: AcmeSigningEngine

    async def issue_certificate(self, *, csr_der: bytes, sans: List[str]) -> Dict[str, Any]:
        return await self.engine.issue_certificate(csr_der=csr_der, sans=sans)
