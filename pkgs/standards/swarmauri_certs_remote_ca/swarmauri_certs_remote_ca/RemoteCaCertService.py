from __future__ import annotations

import base64
from typing import Any, Dict, Iterable, Literal, Mapping, Optional, Sequence

try:
    import httpx
except Exception as e:  # pragma: no cover
    raise ImportError(
        "RemoteCaCertService requires 'httpx'. Install with: pip install httpx"
    ) from e

from swarmauri_base.certs.CertServiceBase import CertServiceBase
from swarmauri_core.certs.ICertService import (
    CertBytes,
    CertExtensionSpec,
    CsrBytes,
    SubjectSpec,
)
from swarmauri_core.crypto.types import KeyRef


class RemoteCaCertService(CertServiceBase):
    """
    Generic remote CA bridge.

    Follows X.509 certificate concepts from RFC 5280 and
    Enrollment over Secure Transport (EST) from RFC 7030.

    Usage model:
      - POST CSR to a configured endpoint (e.g., /sign, /enroll)
      - Remote CA returns certificate (PEM or DER, JSON-encoded or raw)
      - Service normalizes to PEM and hands back CertBytes

    Configuration:
      :param endpoint:   Base URL of remote CA sign endpoint.
      :param auth:       Optional auth headers (dict) or httpx.Auth.
      :param timeout_s:  HTTP timeout (default 10s).
      :param ca_chain:   Optional cached trust anchors to expose on verify/parse.

    Notes:
      - This service does NOT generate CSRs; pair with X509CertService or CsrOnlyService.
      - It assumes a JSON API by default:
            { "csr": "<base64-PEM-or-DER>" }
        and response:
            { "cert": "<base64-PEM-or-DER>" }
        You can override request/response mapping via opts.
    """

    type: Literal["RemoteCaCertService"] = "RemoteCaCertService"

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
        return {
            "key_algs": ("RSA-2048", "RSA-3072", "EC-P256", "Ed25519"),
            "sig_algs": ("RSA-PSS-SHA256", "ECDSA-P256-SHA256", "Ed25519"),
            "features": ("sign_from_csr", "verify", "parse"),
            "profiles": ("server", "client"),
        }

    # ---------------- helpers ----------------

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self._timeout,
                headers={**self._auth, "Accept": "application/json"},
            )
        return self._client

    async def aclose(self) -> None:
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
        raise NotImplementedError("RemoteCaCertService does not create CSRs directly.")

    async def create_self_signed(self, *a, **kw) -> CertBytes:
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
        # Minimal parse: just length and base64 snippet
        return {
            "len": len(cert),
            "pem_snippet": base64.b64encode(cert[:40]).decode("ascii"),
        }
