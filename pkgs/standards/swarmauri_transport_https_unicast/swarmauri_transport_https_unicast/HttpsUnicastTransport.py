from __future__ import annotations

import base64
import hashlib
import hmac
import ssl
from dataclasses import dataclass
from typing import Any, Literal, Mapping

import httpx
from pydantic import Field, PrivateAttr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.transports import TransportBase
from swarmauri_certs_x509verify import X509VerifyService
from swarmauri_cipher_suite_tls13 import Tls13CipherSuite
from swarmauri_core.crypto.types import JWAAlg
from swarmauri_core.transports import (
    AddressScheme,
    Cast,
    Feature,
    IOModel,
    Protocol,
    SecurityMode,
    TransportCapabilities,
)
from swarmauri_middleware_httpsig import HttpSigMiddleware
from swarmauri_signing_jws import JwsSignerVerifier

Bytes = bytes
Headers = dict[str, str]
JwsKey = Mapping[str, Any]


@dataclass(frozen=True)
class HttpsSecurityPolicy:
    """Application-layer security material applied around HTTPS requests."""

    bearer_token: str | None = None
    http_signature_secret: str | bytes | None = None
    http_signature_header: str = "X-Signature"
    request_jws_key: JwsKey | None = None
    request_jws_kid: str | None = None
    request_jws_header: str = "X-Body-JWS"
    response_jws_key: JwsKey | None = None
    response_jws_header: str = "X-Response-JWS"
    jws_alg: JWAAlg = JWAAlg.HS256


@dataclass(frozen=True)
class HttpsTransportEvidence:
    """Verification evidence captured by a secure HTTPS request."""

    status_code: int | None = None
    response_jws_verified: bool = False
    certificate_valid: bool | None = None
    certificate_subject: str | None = None
    cipher_suite: str = "tls13"
    cipher_alg: str | None = None


def _secret_bytes(secret: str | bytes) -> bytes:
    return secret.encode("utf-8") if isinstance(secret, str) else secret


def http_signature(secret: str | bytes, body: bytes) -> str:
    """Return the HMAC-SHA256 signature used by ``HttpSigMiddleware``."""

    return base64.b64encode(
        hmac.new(_secret_bytes(secret), body, hashlib.sha256).digest()
    ).decode("ascii")


@ComponentBase.register_type(TransportBase, "HttpsUnicastTransport")
class HttpsUnicastTransport(TransportBase):
    """HTTPS unicast transport with Swarmauri trust and request-signing policy."""

    type: Literal["HttpsUnicastTransport"] = "HttpsUnicastTransport"

    base_url: str = ""
    verify: bool | str | ssl.SSLContext = True
    timeout: float = 10.0
    trust_env: bool = False
    security_policy: HttpsSecurityPolicy = Field(
        default_factory=HttpsSecurityPolicy
    )
    require_response_jws: bool = False
    httpx_transport: httpx.AsyncBaseTransport | None = Field(
        default=None, exclude=True
    )

    _client: httpx.AsyncClient | None = PrivateAttr(default=None)
    _jws: JwsSignerVerifier = PrivateAttr(default_factory=JwsSignerVerifier)
    _cipher_suite: Tls13CipherSuite = PrivateAttr(
        default_factory=Tls13CipherSuite
    )
    _last_evidence: HttpsTransportEvidence = PrivateAttr(
        default_factory=HttpsTransportEvidence
    )

    def supports(self) -> TransportCapabilities:
        return TransportCapabilities(
            protocols=frozenset({Protocol.HTTP1, Protocol.TLS}),
            io=IOModel.STREAM,
            casts=frozenset({Cast.UNICAST}),
            features=frozenset(
                {
                    Feature.RELIABLE,
                    Feature.ORDERED,
                    Feature.ENCRYPTED,
                    Feature.AUTHENTICATED,
                }
            ),
            security=SecurityMode.TLS,
            schemes=frozenset({AddressScheme.HTTPS}),
        )

    @property
    def last_evidence(self) -> HttpsTransportEvidence:
        return self._last_evidence

    @property
    def cipher_descriptor(self) -> Mapping[str, Any]:
        return self._cipher_suite.normalize(op="encrypt")

    def allowed_tls_cipher(self, cipher_name: str) -> bool:
        return cipher_name in set(self._cipher_suite.supports()["encrypt"])

    def http_signature_middleware(self) -> HttpSigMiddleware:
        secret = self.security_policy.http_signature_secret
        if secret is None:
            raise ValueError("http_signature_secret is required")
        if isinstance(secret, bytes):
            secret = secret.decode("utf-8")
        return HttpSigMiddleware(
            secret_key=secret,
            header_name=self.security_policy.http_signature_header,
        )

    async def verify_certificate(
        self,
        cert_pem: bytes | str,
        *,
        trust_roots: list[bytes | str] | None = None,
    ) -> dict[str, Any]:
        result = await X509VerifyService().verify_cert(
            cert_pem, trust_roots=trust_roots
        )
        self._last_evidence = HttpsTransportEvidence(
            certificate_valid=bool(result.get("valid")),
            certificate_subject=result.get("subject"),
            cipher_suite=self._cipher_suite.suite_id(),
            cipher_alg=self.cipher_descriptor["alg"],
        )
        return result

    async def prepare_headers(
        self,
        body: bytes,
        headers: Headers | None = None,
        *,
        bearer_token: str | None = None,
        http_signature_secret: str | bytes | None = None,
        request_jws_key: JwsKey | None = None,
    ) -> Headers:
        policy = self.security_policy
        prepared = dict(headers or {})

        token = (
            bearer_token if bearer_token is not None else policy.bearer_token
        )
        if token:
            prepared.setdefault("Authorization", f"Bearer {token}")

        secret = (
            http_signature_secret
            if http_signature_secret is not None
            else policy.http_signature_secret
        )
        if secret is not None:
            prepared[policy.http_signature_header] = http_signature(
                secret, body
            )

        jws_key = (
            request_jws_key
            if request_jws_key is not None
            else policy.request_jws_key
        )
        if jws_key is not None:
            prepared[policy.request_jws_header] = await self._jws.sign_compact(
                payload=body,
                alg=policy.jws_alg,
                key=jws_key,
                kid=policy.request_jws_kid,
                typ="JWS",
            )

        return prepared

    async def verify_body_jws(
        self,
        compact_jws: str,
        body: bytes,
        *,
        hmac_keys: list[JwsKey] | None = None,
    ) -> None:
        keys = hmac_keys or [self.security_policy.response_jws_key]
        usable_keys = [key for key in keys if key is not None]
        result = await self._jws.verify_compact(
            compact_jws,
            hmac_keys=usable_keys,
            alg_allowlist=[self.security_policy.jws_alg],
        )
        if result.payload != body:
            raise ValueError("JWS payload does not match body")

    async def _start_server(self, **bind_kwargs: Any) -> None:
        raise NotImplementedError(
            "HttpsUnicastTransport provides HTTPS client transport orchestration"
        )

    async def _stop_server(self) -> None:
        return None

    async def _open_client(self, **connect_kwargs: Any) -> None:
        self._client = httpx.AsyncClient(**self._client_kwargs(connect_kwargs))

    async def _close_client(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def request(
        self,
        method: str,
        path: str,
        headers: Headers | None = None,
        body: Bytes = b"",
        **kwargs: Any,
    ) -> tuple[int, Headers, Bytes]:
        request_headers = await self.prepare_headers(body, headers)
        response_jws_verified = False
        client = self._client

        if client is None:
            async with httpx.AsyncClient(
                **self._client_kwargs({})
            ) as one_shot:
                response = await one_shot.request(
                    method,
                    path,
                    headers=request_headers,
                    content=body,
                    **kwargs,
                )
        else:
            response = await client.request(
                method, path, headers=request_headers, content=body, **kwargs
            )

        response_jws = response.headers.get(
            self.security_policy.response_jws_header
        )
        if response_jws:
            await self.verify_body_jws(response_jws, response.content)
            response_jws_verified = True
        elif self.require_response_jws:
            raise ValueError(
                f"missing {self.security_policy.response_jws_header} response header"
            )

        descriptor = self.cipher_descriptor
        self._last_evidence = HttpsTransportEvidence(
            status_code=response.status_code,
            response_jws_verified=response_jws_verified,
            cipher_suite=self._cipher_suite.suite_id(),
            cipher_alg=descriptor["alg"],
        )
        return response.status_code, dict(response.headers), response.content

    def _client_kwargs(self, overrides: Mapping[str, Any]) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "verify": overrides.get("verify", self.verify),
            "timeout": overrides.get("timeout", self.timeout),
            "trust_env": overrides.get("trust_env", self.trust_env),
        }
        base_url = overrides.get("base_url", self.base_url)
        if base_url:
            kwargs["base_url"] = base_url
        transport = overrides.get("transport", self.httpx_transport)
        if transport is not None:
            kwargs["transport"] = transport
        return kwargs
