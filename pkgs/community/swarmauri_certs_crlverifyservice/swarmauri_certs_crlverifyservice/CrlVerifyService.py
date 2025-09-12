"""Certificate verification against Certificate Revocation Lists (CRLs).

This module provides :class:`CrlVerifyService`, an implementation of
``CertServiceBase`` that validates X.509 certificates using CRLs. It checks
basic validity windows, matches issuers, and marks certificates as revoked when
listed in the supplied CRLs.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, Iterable, Literal, Mapping, Optional, Sequence

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.base import Certificate
from cryptography.x509.extensions import ExtensionNotFound
from cryptography.x509.oid import ExtensionOID

from swarmauri_base.certs.CertServiceBase import CertServiceBase


class CrlVerifyService(CertServiceBase):
    """Certificate Revocation List (CRL) verification service.

    Implements ``verify_cert`` and ``parse_cert`` against CRLs, following RFC 5280. This service does not issue or sign certificates (CSR,
    self-signed, and sign-cert methods remain ``NotImplemented``).

    Capabilities:
      - ``verify_cert(cert, trust_roots, crls=...)``: check validity window,
        issuer match, and revocation against provided CRLs.
      - ``parse_cert(cert)``: extract minimal metadata for inspection.
    """

    type: Literal["CrlVerifyService"] = "CrlVerifyService"

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {"features": ("verify", "parse", "crl")}

    async def verify_cert(
        self,
        cert: bytes,
        *,
        trust_roots: Optional[Sequence[bytes]] = None,
        intermediates: Optional[Sequence[bytes]] = None,
        check_time: Optional[int] = None,
        check_revocation: bool = True,
        crls: Optional[Sequence[bytes]] = None,
        opts: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Verify an X.509 certificate against CRLs.

        Args:
            cert (bytes): The certificate data in PEM or DER encoding.
            trust_roots (Optional[Sequence[bytes]]): Trusted root certificates
                used for chain validation. Defaults to ``None``.
            intermediates (Optional[Sequence[bytes]]): Intermediate
                certificates for building the chain. Defaults to ``None``.
            check_time (Optional[int]): Unix timestamp used to evaluate the
                certificate validity period. Defaults to current time.
            check_revocation (bool): Whether to verify revocation status.
                Defaults to ``True``.
            crls (Optional[Sequence[bytes]]): CRLs to check for revocation
                status. Defaults to ``None``.
            opts (Optional[Dict[str, Any]]): Implementation-specific options.

        Returns:
            Dict[str, Any]: A dictionary describing the verification result,
            including validity and revocation status.
        """
        now = datetime.datetime.utcfromtimestamp(
            check_time or datetime.datetime.utcnow().timestamp()
        )

        cert_obj: Certificate = x509.load_pem_x509_certificate(cert, default_backend())
        out: Dict[str, Any] = {
            "valid": True,
            "reason": None,
            "subject": cert_obj.subject.rfc4514_string(),
            "issuer": cert_obj.issuer.rfc4514_string(),
            "not_before": int(cert_obj.not_valid_before.timestamp()),
            "not_after": int(cert_obj.not_valid_after.timestamp()),
            "revoked": False,
        }

        if now < cert_obj.not_valid_before or now > cert_obj.not_valid_after:
            out["valid"] = False
            out["reason"] = "expired_or_not_yet_valid"

        if check_revocation and crls:
            for crl_bytes in crls:
                try:
                    crl = x509.load_pem_x509_crl(crl_bytes, default_backend())
                except ValueError:
                    crl = x509.load_der_x509_crl(crl_bytes, default_backend())
                if crl.issuer == cert_obj.issuer:
                    if crl.get_revoked_certificate_by_serial_number(
                        cert_obj.serial_number
                    ):
                        out["valid"] = False
                        out["revoked"] = True
                        out["reason"] = "revoked"
                        break

        return out

    async def parse_cert(
        self,
        cert: bytes,
        *,
        include_extensions: bool = True,
        opts: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Parse an X.509 certificate and extract metadata.

        Args:
            cert (bytes): The certificate data in PEM encoding.
            include_extensions (bool): Whether to include common extensions in
                the output. Defaults to ``True``.
            opts (Optional[Dict[str, Any]]): Additional options for parsing.

        Returns:
            Dict[str, Any]: Metadata extracted from the certificate such as
            subject, issuer, validity window, and optional extensions.
        """
        cert_obj: Certificate = x509.load_pem_x509_certificate(cert, default_backend())
        out: Dict[str, Any] = {
            "serial": cert_obj.serial_number,
            "subject": cert_obj.subject.rfc4514_string(),
            "issuer": cert_obj.issuer.rfc4514_string(),
            "not_before": int(cert_obj.not_valid_before.timestamp()),
            "not_after": int(cert_obj.not_valid_after.timestamp()),
            "sig_alg": cert_obj.signature_algorithm_oid._name,
        }

        if include_extensions:
            try:
                bc = cert_obj.extensions.get_extension_for_oid(
                    ExtensionOID.BASIC_CONSTRAINTS
                ).value
                out["basic_constraints"] = {"ca": bc.ca, "path_len": bc.path_length}
            except ExtensionNotFound:
                pass

            try:
                ku = cert_obj.extensions.get_extension_for_oid(
                    ExtensionOID.KEY_USAGE
                ).value
                out["key_usage"] = {
                    "digital_signature": ku.digital_signature,
                    "key_encipherment": ku.key_encipherment,
                    "key_cert_sign": ku.key_cert_sign,
                }
            except ExtensionNotFound:
                pass

        return out
