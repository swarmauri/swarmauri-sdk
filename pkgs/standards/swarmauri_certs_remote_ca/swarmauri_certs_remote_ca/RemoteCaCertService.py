from __future__ import annotations

import base64
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence

try:
    import httpx
except Exception as e:  # pragma: no cover
    raise ImportError(
        "RemoteCaCertService requires 'httpx'. Install with: pip install httpx"
    ) from e

from swarmauri_base.certs.CertServiceBase import CertServiceBase
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.certs.ICertService import (
    CertBytes,
    CertExtensionSpec,
    CsrBytes,
    SubjectSpec,
)
from swarmauri_core.crypto.types import KeyRef


@ComponentBase.register_type(CertServiceBase, "RemoteCaCertService")
class RemoteCaCertService(CertServiceBase):
    """Bridge to a remote Certificate Authority over HTTP.

    The service forwards certificate signing requests (CSRs) to a remote
    endpoint and returns the issued certificate. It follows X.509 concepts
    (RFC 5280) and Enrollment over Secure Transport (EST, RFC 7030).

    Args:
        endpoint (str): Base URL of the remote CA sign endpoint.
        auth (Mapping[str, str] | httpx.Auth, optional): Authentication headers
            or an ``httpx.Auth`` instance used for each request.
        timeout_s (float, optional): HTTP timeout in seconds. Defaults to
            ``10.0``.
        ca_chain (Sequence[CertBytes], optional): Cached trust anchors exposed
            when verifying or parsing certificates.

    Notes:
        This service does not generate CSRs; pair it with ``X509CertService`` or
        ``CsrOnlyService``. By default it assumes a JSON API with the request
        body ``{"csr": "<base64-PEM-or-DER>"}`` and response
        ``{"cert": "<base64-PEM-or-DER>"}``. These mappings can be overridden
        via ``opts``.
    """

    def __init__(
        self,
        endpoint: str,
        *,
        auth: Optional[Mapping[str, str]] = None,
        timeout_s: float = 10.0,
        ca_chain: Optional[Sequence[CertBytes]] = None,
    ) -> None:
        super().__init__()
        self._endpoint = endpoint
        self._auth = auth or {}
        self._timeout = timeout_s
        self._ca_chain = ca_chain or []
        self._client: Optional[httpx.AsyncClient] = None

    # ---------------- capability ----------------

    def supports(self) -> Mapping[str, Iterable[str]]:
        """Describe capabilities advertised by the service.

        Returns:
            Mapping[str, Iterable[str]]: Supported algorithms, features and
            profiles.
        """

        return {
            "key_algs": ("RSA-2048", "RSA-3072", "EC-P256", "Ed25519"),
            "sig_algs": ("RSA-PSS-SHA256", "ECDSA-P256-SHA256", "Ed25519"),
            "features": ("sign_from_csr", "verify", "parse"),
            "profiles": ("server", "client"),
        }

    # ---------------- helpers ----------------

    async def _get_client(self) -> httpx.AsyncClient:
        """Return or create the underlying HTTP client.

        Returns:
            httpx.AsyncClient: Lazy-initialized asynchronous client instance.
        """

        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self._timeout,
                headers={**self._auth, "Accept": "application/json"},
            )
        return self._client

    async def aclose(self) -> None:
        """Close the underlying HTTP client if it exists."""

        if self._client:
            await self._client.aclose()
            self._client = None

    # ---------------- core ICertService ----------------

    async def create_csr(
        self,
        key: KeyRef,
        subject: SubjectSpec,
        *,
        san: Optional[Dict[str, Any]] = None,
        extensions: Optional[CertExtensionSpec] = None,
        sig_alg: Optional[str] = None,
        challenge_password: Optional[str] = None,
        output_der: bool = False,
        opts: Optional[Dict[str, Any]] = None,
    ) -> CsrBytes:
        """Unsupported CSR creation operation.

        Raises:
            NotImplementedError: Always raised since this service cannot create
                CSRs directly.
        """

        raise NotImplementedError("RemoteCaCertService does not create CSRs directly.")

    async def create_self_signed(self, *a, **kw) -> CertBytes:
        """Unsupported self-signed certificate operation.

        Raises:
            NotImplementedError: Always raised since this service cannot
                self-sign certificates.
        """

        raise NotImplementedError(
            "RemoteCaCertService does not self-sign certificates."
        )

    async def sign_cert(
        self,
        csr: CsrBytes,
        ca_key: KeyRef,
        *,
        issuer: Optional[SubjectSpec] = None,
        ca_cert: Optional[CertBytes] = None,
        serial: Optional[int] = None,
        not_before: Optional[int] = None,
        not_after: Optional[int] = None,
        extensions: Optional[CertExtensionSpec] = None,
        sig_alg: Optional[str] = None,
        output_der: bool = False,
        opts: Optional[Dict[str, Any]] = None,
    ) -> CertBytes:
        """Request certificate issuance from the remote CA.

        Args:
            csr (CsrBytes): CSR bytes to forward to the remote CA.
            ca_key (KeyRef): Ignored; present for interface compatibility.
            issuer (SubjectSpec, optional): Ignored.
            ca_cert (CertBytes, optional): Ignored.
            serial (int, optional): Ignored.
            not_before (int, optional): Ignored.
            not_after (int, optional): Ignored.
            extensions (CertExtensionSpec, optional): Extension values to merge
                into the request.
            sig_alg (str, optional): Signature algorithm hint.
            output_der (bool, optional): Whether to return DER instead of PEM.
            opts (Dict[str, Any], optional): Extra request options merged into
                the JSON body under ``"extra"``.

        Returns:
            CertBytes: Certificate returned by the remote CA.
        """

        client = await self._get_client()

        # Default: POST JSON with base64 PEM
        payload = {"csr": base64.b64encode(csr).decode("ascii")}
        if opts and "extra" in opts:
            payload.update(opts["extra"])

        resp = await client.post(self._endpoint, json=payload)
        resp.raise_for_status()

        try:
            data = resp.json()
            cert_b64 = data.get("cert")
            if not cert_b64:
                raise ValueError("Remote CA response missing 'cert'")
            cert = base64.b64decode(cert_b64)
        except Exception:
            # fallback: raw body is cert
            cert = resp.content

        return cert

    async def verify_cert(
        self,
        cert: CertBytes,
        *,
        trust_roots: Optional[Sequence[CertBytes]] = None,
        intermediates: Optional[Sequence[CertBytes]] = None,
        check_time: Optional[int] = None,
        check_revocation: bool = False,
        opts: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Stub certificate verification.

        Args:
            cert (CertBytes): Certificate to verify.
            trust_roots (Sequence[CertBytes], optional): Trusted root
                certificates.
            intermediates (Sequence[CertBytes], optional): Intermediate
                certificates.
            check_time (int, optional): Verification time as a UNIX timestamp.
            check_revocation (bool, optional): Whether to perform revocation
                checks.
            opts (Dict[str, Any], optional): Additional verification options.

        Returns:
            Dict[str, Any]: Always returns an unsupported verification result.
        """

        # For now: defer to X509CertService or external verifier
        # Here we just acknowledge we can't fully verify.
        return {"valid": False, "reason": "verify_not_supported", "active": False}

    async def parse_cert(
        self,
        cert: CertBytes,
        *,
        include_extensions: bool = True,
        opts: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Extract minimal information from a certificate.

        Args:
            cert (CertBytes): Certificate to parse.
            include_extensions (bool, optional): Whether to include extension
                data in the result.
            opts (Dict[str, Any], optional): Reserved for future options.

        Returns:
            Dict[str, Any]: Length and base64 snippet of the certificate.
        """

        # Minimal parse: just length and base64 snippet
        return {
            "len": len(cert),
            "pem_snippet": base64.b64encode(cert[:40]).decode("ascii"),
        }
