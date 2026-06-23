# ruff: noqa: E402
from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import queue
import ssl
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
for relative in (
    "pkgs/core",
    "pkgs/base",
    "pkgs/standards/swarmauri_certs_self_signed",
    "pkgs/standards/swarmauri_certs_x509verify",
    "pkgs/standards/swarmauri_cipher_suite_tls13",
    "pkgs/standards/swarmauri_middleware_httpsig",
    "pkgs/standards/swarmauri_signing_jws",
    "pkgs/standards/swarmauri_tokens_jwt",
):
    sys.path.insert(0, str(ROOT / relative))

import httpx
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtensionOID
from swarmauri_certs_self_signed import SelfSignedCertificate
from swarmauri_certs_x509verify import X509VerifyService
from swarmauri_cipher_suite_tls13 import Tls13CipherSuite
from swarmauri_core.crypto.types import ExportPolicy, JWAAlg, KeyRef, KeyType, KeyUse
from swarmauri_core.key_providers.IKeyProvider import IKeyProvider
from swarmauri_core.key_providers.types import KeySpec
from swarmauri_middleware_httpsig import HttpSigMiddleware
from swarmauri_signing_jws import JwsSignerVerifier
from swarmauri_tokens_jwt import JWTTokenService

ISSUER = "https://issuer.local"
AUDIENCE = "https://127.0.0.1/demo"
TRUST_SECRET = b"local-demo-trust-secret-32-bytes!!"
BODY_SIGNING_KEY = {"kind": "raw", "key": TRUST_SECRET, "kid": "body-hmac.1"}


class DemoKeyProvider(IKeyProvider):
    def __init__(self, secret: bytes) -> None:
        self.secret = secret
        self.kid = "demo-hs"
        self.version = 1

    def supports(self) -> dict[str, list[str]]:
        return {"algs": ["HS256"], "features": ["jwks", "sign", "verify"]}

    async def create_key(self, spec: KeySpec) -> KeyRef:
        raise NotImplementedError

    async def import_key(
        self, spec: KeySpec, material: bytes, *, public: bytes | None = None
    ) -> KeyRef:
        raise NotImplementedError

    async def rotate_key(
        self, kid: str, *, spec_overrides: dict | None = None
    ) -> KeyRef:
        raise NotImplementedError

    async def destroy_key(self, kid: str, version: int | None = None) -> bool:
        return False

    async def get_key(
        self, kid: str, version: int | None = None, *, include_secret: bool = False
    ) -> KeyRef:
        if kid != self.kid:
            raise KeyError(kid)
        return KeyRef(
            kid=self.kid,
            version=version or self.version,
            type=KeyType.OPAQUE,
            uses=(KeyUse.SIGN, KeyUse.VERIFY),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            material=self.secret if include_secret else None,
        )

    async def list_versions(self, kid: str) -> tuple[int, ...]:
        if kid != self.kid:
            return ()
        return (self.version,)

    async def get_public_jwk(self, kid: str, version: int | None = None) -> dict:
        jwks = await self.jwks()
        return jwks["keys"][0]

    async def jwks(self, *, prefix_kids: str | None = None) -> dict:
        key = base64.urlsafe_b64encode(self.secret).rstrip(b"=").decode("ascii")
        kid = f"{self.kid}.{self.version}"
        if prefix_kids and not kid.startswith(prefix_kids):
            return {"keys": []}
        return {"keys": [{"kty": "oct", "kid": kid, "k": key}]}

    async def random_bytes(self, n: int) -> bytes:
        return b"\x00" * n

    async def hkdf(self, ikm: bytes, *, salt: bytes, info: bytes, length: int) -> bytes:
        return hmac.new(salt, ikm + info, hashlib.sha256).digest()[:length]


class SecurityContext:
    def __init__(self, cert_pem: bytes) -> None:
        self.http_sig = HttpSigMiddleware(
            secret_key=TRUST_SECRET.decode("ascii"),
            header_name="X-Signature",
        )
        self.jws = JwsSignerVerifier()
        self.key_provider = DemoKeyProvider(TRUST_SECRET)
        self.jwt = JWTTokenService(self.key_provider, default_issuer=ISSUER)
        self.cipher_suite = Tls13CipherSuite()
        self.cipher_descriptor = self.cipher_suite.normalize(op="encrypt")
        self.cert_preflight = asyncio.run(
            X509VerifyService().verify_cert(cert_pem, trust_roots=[cert_pem])
        )

    async def mint_token(self) -> str:
        return await self.jwt.mint(
            {"role": "demo-client"},
            alg=JWAAlg.HS256,
            kid=self.key_provider.kid,
            audience=AUDIENCE,
            subject="client-thread",
            scope="orders:create",
        )

    async def sign_body(self, body: bytes) -> str:
        return await self.jws.sign_compact(
            payload=body,
            alg=JWAAlg.HS256,
            key=BODY_SIGNING_KEY,
            kid=BODY_SIGNING_KEY["kid"],
            typ="JWS",
        )

    async def verify_body_jws(self, compact_jws: str, body: bytes) -> None:
        result = await self.jws.verify_compact(
            compact_jws,
            hmac_keys=[BODY_SIGNING_KEY],
            alg_allowlist=[JWAAlg.HS256],
        )
        if result.payload != body:
            raise ValueError("JWS payload does not match HTTP body")

    async def verify_jwt(self, token: str) -> dict[str, Any]:
        return await self.jwt.verify(token, issuer=ISSUER, audience=AUDIENCE)

    def verify_http_signature(self, signature: str | None, body: bytes) -> None:
        if not signature:
            raise ValueError("missing HTTP signature")
        expected = http_signature(body)
        if not hmac.compare_digest(signature, expected):
            raise ValueError("invalid HTTP signature")

    def allowed_tls_cipher(self, cipher_name: str) -> bool:
        return cipher_name in set(self.cipher_suite.supports()["encrypt"])


class DemoHttpHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_POST(self) -> None:
        ctx: SecurityContext = self.server.security_context  # type: ignore[attr-defined]
        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length)
        checks: list[str] = []

        try:
            cipher = self.connection.cipher()
            tls_cipher = cipher[0] if cipher else "unknown"
            tls_version = self.connection.version()
            if not ctx.allowed_tls_cipher(tls_cipher):
                raise ValueError(f"TLS cipher not allowed by suite: {tls_cipher}")
            checks.append("tls_cipher_allowed")

            ctx.verify_http_signature(self.headers.get(ctx.http_sig.header_name), body)
            checks.append("http_signature_valid")

            authorization = self.headers.get("Authorization", "")
            if not authorization.startswith("Bearer "):
                raise ValueError("missing bearer token")
            claims = asyncio.run(ctx.verify_jwt(authorization.removeprefix("Bearer ")))
            checks.append("jwt_valid")

            asyncio.run(ctx.verify_body_jws(self.headers.get("X-Body-JWS", ""), body))
            checks.append("jws_body_valid")
            checks.append("x509_ip_san_trust_preflight_valid")

            response_payload = {
                "ok": True,
                "server_thread": threading.current_thread().name,
                "path": self.path,
                "client_subject": claims["sub"],
                "scope": claims["scope"],
                "tls_version": tls_version,
                "tls_cipher": tls_cipher,
                "cipher_suite": ctx.cipher_descriptor.get(
                    "suite", ctx.cipher_suite.suite_id()
                ),
                "cipher_alg": ctx.cipher_descriptor["alg"],
                "certificate_subject": ctx.cert_preflight["subject"],
                "checks": checks,
                "request": json.loads(body),
            }
            self._send_json(200, response_payload, ctx)
        except Exception as exc:
            self._send_json(
                401, {"ok": False, "error": str(exc), "checks": checks}, ctx
            )

    def _send_json(
        self, status: int, payload: dict[str, Any], ctx: SecurityContext
    ) -> None:
        response_body = json.dumps(
            payload, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        response_jws = asyncio.run(ctx.sign_body(response_body))
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_body)))
        self.send_header("X-Response-JWS", response_jws)
        self.end_headers()
        self.wfile.write(response_body)

    def log_message(self, format: str, *args: Any) -> None:
        return None


def issue_loopback_ip_certificate(tmp_dir: Path) -> tuple[Path, Path, bytes, list[str]]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    key_ref = KeyRef(
        kid="loopback-ip-tls",
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=private_pem,
    )
    cert_pem = SelfSignedCertificate.tls_server(
        "127.0.0.1",
        ip_addrs=("127.0.0.1",),
        lifetime_days=30,
    ).issue(key_ref)
    cert = x509.load_pem_x509_certificate(cert_pem)
    san = cert.extensions.get_extension_for_oid(
        ExtensionOID.SUBJECT_ALTERNATIVE_NAME
    ).value
    ip_sans = [str(ip) for ip in san.get_values_for_type(x509.IPAddress)]

    key_path = tmp_dir / "loopback-ip.key.pem"
    cert_path = tmp_dir / "loopback-ip.cert.pem"
    key_path.write_bytes(private_pem)
    cert_path.write_bytes(cert_pem)
    return cert_path, key_path, cert_pem, ip_sans


def make_ip_tls_server(
    cert_path: Path, key_path: Path, context: SecurityContext
) -> HTTPServer:
    httpd = HTTPServer(("127.0.0.1", 0), DemoHttpHandler)
    httpd.security_context = context  # type: ignore[attr-defined]

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3
    ssl_context.load_cert_chain(certfile=cert_path, keyfile=key_path)
    httpd.socket = ssl_context.wrap_socket(httpd.socket, server_side=True)
    return httpd


def http_signature(body: bytes) -> str:
    return base64.b64encode(
        hmac.new(TRUST_SECRET, body, hashlib.sha256).digest()
    ).decode("ascii")


def run_ip_client(
    port: int, cert_path: Path, context: SecurityContext
) -> dict[str, Any]:
    body = json.dumps(
        {"order_id": "ord_ip_1001", "amount": 99.5},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    token = asyncio.run(context.mint_token())
    body_jws = asyncio.run(context.sign_body(body))

    with httpx.Client(verify=str(cert_path), trust_env=False, timeout=10.0) as client:
        response = client.post(
            f"https://127.0.0.1:{port}/secure/ip-orders",
            content=body,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "X-Body-JWS": body_jws,
                "X-Signature": http_signature(body),
            },
        )

    asyncio.run(
        context.verify_body_jws(response.headers["X-Response-JWS"], response.content)
    )
    response.raise_for_status()
    return {
        "client_thread": threading.current_thread().name,
        "status_code": response.status_code,
        "response_jws_verified": True,
        "response": response.json(),
    }


def main() -> None:
    tmp_root = ROOT / "tmp"
    tmp_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="http-ip-trust-demo-", dir=tmp_root) as td:
        temp_dir = Path(td)
        cert_path, key_path, cert_pem, ip_sans = issue_loopback_ip_certificate(temp_dir)
        context = SecurityContext(cert_pem)
        server = make_ip_tls_server(cert_path, key_path, context)
        port = server.server_address[1]
        ready = threading.Event()
        results: queue.Queue[tuple[str, Any]] = queue.Queue()

        def server_worker() -> None:
            ready.set()
            server.serve_forever(poll_interval=0.05)

        def client_worker() -> None:
            try:
                ready.wait(timeout=5)
                results.put(("ok", run_ip_client(port, cert_path, context)))
            except Exception as exc:
                results.put(("error", repr(exc)))

        server_thread = threading.Thread(
            target=server_worker, name="demo-ip-http-server", daemon=True
        )
        client_thread = threading.Thread(
            target=client_worker, name="demo-ip-httpx-client"
        )

        server_thread.start()
        client_thread.start()
        client_thread.join(timeout=15)
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=15)

        if client_thread.is_alive():
            raise RuntimeError("client thread did not finish")
        status, payload = results.get_nowait()
        if status != "ok":
            raise RuntimeError(payload)

        summary = {
            "cert_preflight_valid": context.cert_preflight["valid"],
            "ip_subject_alt_names": ip_sans,
            "server_thread_alive_after_shutdown": server_thread.is_alive(),
            "trusted_url": f"https://127.0.0.1:{port}/secure/ip-orders",
            **payload,
        }
        print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
