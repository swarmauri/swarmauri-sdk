from __future__ import annotations

from typing import Optional, Literal
from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.certs.ICertService import ICertService


class CertServiceBase(ICertService, ComponentBase):
    """Abstract base class for certificate services compliant with RFC 5280 and RFC 2986."""

    resource: Optional[str] = Field(default=ResourceTypes.CRYPTO.value, frozen=True)
    type: Literal["CertServiceBase"] = "CertServiceBase"

    # Capability probe
    def supports(self):
        raise NotImplementedError("supports() must be implemented by subclass")

    # CSR
    async def create_csr(self, *a, **kw):
        raise NotImplementedError("create_csr() must be implemented by subclass")

    # Self-signed certificate
    async def create_self_signed(self, *a, **kw):
        raise NotImplementedError(
            "create_self_signed() must be implemented by subclass"
        )

    # CA-signed certificate
    async def sign_cert(self, *a, **kw):
        raise NotImplementedError("sign_cert() must be implemented by subclass")

    # Verification
    async def verify_cert(self, *a, **kw):
        raise NotImplementedError("verify_cert() must be implemented by subclass")

    # Parsing
    async def parse_cert(self, *a, **kw):
        raise NotImplementedError("parse_cert() must be implemented by subclass")
