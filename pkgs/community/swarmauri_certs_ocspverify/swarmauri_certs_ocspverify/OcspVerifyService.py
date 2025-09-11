from __future__ import annotations

from typing import Any, Dict, Iterable, Literal, Mapping, Optional, Sequence

import httpx
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.x509.ocsp import OCSPRequestBuilder, load_der_ocsp_response

from swarmauri_base.certs.CertServiceBase import CertServiceBase


class OcspVerifyService(CertServiceBase):
    """OCSP verification service compliant with RFC 6960 and RFC 5280.

    - Implements ``verify_cert`` using OCSP responders advertised in the certificate's
      Authority Information Access extension.
    - ``parse_cert`` extracts subject/issuer, dates, and OCSP URLs.
    - ``create_csr``/``create_self_signed``/``sign_cert`` are not implemented (verify-only service).
    """

    type: Literal["OcspVerifyService"] = "OcspVerifyService"

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {"features": ("verify", "parse", "ocsp")}

    async def create_csr(self, *a, **kw):
        raise NotImplementedError("OcspVerifyService does not create CSRs.")

    async def create_self_signed(self, *a, **kw):
        raise NotImplementedError("OcspVerifyService does not issue certificates.")

    async def sign_cert(self, *a, **kw):
        raise NotImplementedError("OcspVerifyService does not sign certificates.")

    async def verify_cert(
        self,
        cert: bytes,
        *,
        trust_roots: Optional[Sequence[bytes]] = None,
        intermediates: Optional[Sequence[bytes]] = None,
        check_time: Optional[int] = None,
        check_revocation: bool = True,
        opts: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        cert_obj = x509.load_pem_x509_certificate(cert, default_backend())
        if not intermediates:
            raise ValueError(
                "OCSP verification requires issuer certificate in 'intermediates'"
            )
        issuer_obj = x509.load_pem_x509_certificate(intermediates[0], default_backend())
        try:
            aia = cert_obj.extensions.get_extension_for_oid(
                x509.ExtensionOID.AUTHORITY_INFORMATION_ACCESS
            )
            ocsp_urls = [
                d.access_location.value
                for d in aia.value
                if d.access_method == x509.AuthorityInformationAccessOID.OCSP
            ]
        except x509.ExtensionNotFound:
            ocsp_urls = []

        if not ocsp_urls:
            return {"valid": False, "reason": "no_ocsp_url", "ocsp_checked": False}

        builder = OCSPRequestBuilder().add_certificate(
            cert_obj, issuer_obj, cert_obj.signature_hash_algorithm
        )
        req = builder.build()
        der_req = req.public_bytes(serialization.Encoding.DER)
        url = ocsp_urls[0]

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                url,
                content=der_req,
                headers={"Content-Type": "application/ocsp-request"},
            )
            resp.raise_for_status()
            ocsp_resp = load_der_ocsp_response(resp.content)

        status = ocsp_resp.certificate_status
        result: Dict[str, Any] = {
            "valid": status == x509.ocsp.OCSPCertStatus.GOOD,
            "reason": None if status == x509.ocsp.OCSPCertStatus.GOOD else str(status),
            "ocsp_checked": True,
            "this_update": ocsp_resp.this_update.timestamp(),
            "next_update": ocsp_resp.next_update.timestamp()
            if ocsp_resp.next_update
            else None,
        }
        return result

    async def parse_cert(
        self,
        cert: bytes,
        *,
        include_extensions: bool = True,
        opts: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        obj = x509.load_pem_x509_certificate(cert, default_backend())
        out: Dict[str, Any] = {
            "subject": obj.subject.rfc4514_string(),
            "issuer": obj.issuer.rfc4514_string(),
            "not_before": int(obj.not_valid_before_utc.timestamp()),
            "not_after": int(obj.not_valid_after_utc.timestamp()),
        }
        if include_extensions:
            try:
                aia = obj.extensions.get_extension_for_oid(
                    x509.ExtensionOID.AUTHORITY_INFORMATION_ACCESS
                )
                ocsp_urls = [
                    d.access_location.value
                    for d in aia.value
                    if d.access_method == x509.AuthorityInformationAccessOID.OCSP
                ]
                out["ocsp_urls"] = ocsp_urls
            except x509.ExtensionNotFound:
                out["ocsp_urls"] = []
        return out
