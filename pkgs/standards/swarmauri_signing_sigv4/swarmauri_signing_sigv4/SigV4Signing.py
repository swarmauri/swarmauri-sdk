from __future__ import annotations

import datetime
import hashlib
import hmac
import urllib.parse
from typing import Any, Iterable, List, Mapping, Optional, Sequence, Tuple

from pydantic import Field

from swarmauri_base.signing.SigningBase import SigningBase
from swarmauri_base.ComponentBase import ResourceTypes
from swarmauri_core.crypto.types import Alg, KeyRef
from swarmauri_core.signing.ISigning import Canon, Envelope
from swarmauri_core.signing.types import Signature


class SigV4Signing(SigningBase):
    """AWS Signature Version 4 (SigV4) signer/verifier."""

    resource: Optional[str] = Field(default=ResourceTypes.CRYPTO.value, frozen=True)
    type: str = "SigV4Signing"

    # ---------- capabilities ----------
    def supports(self) -> Mapping[str, Iterable[str]]:
        return {
            "alg": ("AWS4-HMAC-SHA256",),
            "envelope": ("http-request-v1",),
            "payload": ("bytes-hmac-v1",),
        }

    # ---------- helpers ----------
    @staticmethod
    def _get_key_fields(key: KeyRef) -> Tuple[str, str, Optional[str]]:
        """Extract key fields from a flexible :class:`KeyRef`."""

        def get_first(data: Any, *names: str) -> Optional[str]:
            for name in names:
                if isinstance(data, Mapping) and name in data:
                    return data[name]  # type: ignore[index]
                if hasattr(data, name):
                    return getattr(data, name)
            return None

        akid = get_first(key, "access_key", "akid", "accessKeyId", "AccessKeyId")
        secret = get_first(
            key, "secret_key", "sk", "secretAccessKey", "SecretAccessKey"
        )
        token = get_first(key, "session_token", "token", "SessionToken")
        if not akid or not secret:
            raise ValueError("KeyRef must contain access key id and secret key")
        return akid, secret, token

    @staticmethod
    def _hmac(key_bytes: bytes, msg: str) -> bytes:
        return hmac.new(key_bytes, msg.encode("utf-8"), hashlib.sha256).digest()

    @staticmethod
    def _sha256_hex(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def _canonical_uri(uri: str) -> str:
        # RFC3986 path normalization; AWS allows '/-_.~' unescaped
        return urllib.parse.quote(uri if uri else "/", safe="/-_.~")

    @staticmethod
    def _canonical_query(qs: Mapping[str, Iterable[str]] | None) -> str:
        if not qs:
            return ""
        items: List[Tuple[str, str]] = []
        for key, values in qs.items():
            if values is None:
                items.append((key, ""))
                continue
            for value in values:
                items.append((key, "" if value is None else str(value)))
        items.sort(key=lambda pair: (pair[0], pair[1]))

        def encode(value: str) -> str:
            return urllib.parse.quote(str(value), safe="-_.~")

        return "&".join(f"{encode(k)}={encode(v)}" for k, v in items)

    @staticmethod
    def _canonical_headers(headers: Mapping[str, str]) -> Tuple[str, str]:
        """Return canonical header block and the signed headers list."""

        canonical_lines: List[str] = []
        signed: List[str] = []
        for key, value in headers.items():
            key_lower = key.strip().lower()
            value_clean = " ".join(value.strip().split())
            canonical_lines.append(f"{key_lower}:{value_clean}\n")
            signed.append(key_lower)
        canonical_lines.sort()
        signed.sort()
        return "".join(canonical_lines), ";".join(signed)

    @classmethod
    def _string_to_sign(cls, amz_date: str, scope: str, canonical_request: str) -> str:
        request_hash = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
        return "AWS4-HMAC-SHA256\n" + amz_date + "\n" + scope + "\n" + request_hash

    @classmethod
    def _derive_signing_key(
        cls, secret_key: str, date: str, region: str, service: str
    ) -> bytes:
        k_date = hmac.new(
            ("AWS4" + secret_key).encode("utf-8"), date.encode("utf-8"), hashlib.sha256
        ).digest()
        k_region = hmac.new(k_date, region.encode("utf-8"), hashlib.sha256).digest()
        k_service = hmac.new(k_region, service.encode("utf-8"), hashlib.sha256).digest()
        return hmac.new(k_service, b"aws4_request", hashlib.sha256).digest()

    @classmethod
    def _ensure_scope(cls, scope: Mapping[str, str]) -> Tuple[str, str, str, str]:
        date = scope.get("date") or ""
        region = scope.get("region") or ""
        service = scope.get("service") or ""
        if not (date and region and service):
            raise ValueError("scope must contain {date, region, service}")
        return date, region, service, f"{date}/{region}/{service}/aws4_request"

    # ---------- core (HTTP request) ----------
    async def canonicalize_envelope(
        self,
        env: Envelope,
        *,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        """Build the canonical request bytes for a SigV4 HTTP request envelope."""

        method = str(env["method"]).upper()
        uri = str(env.get("uri", "/"))
        query = env.get("query") or {}
        headers = env.get("headers") or {}
        payload_hash = str(env.get("payload_hash", ""))
        header_lookup = {k.lower(): v for k, v in headers.items()}
        if "host" not in header_lookup:
            raise ValueError("envelope.headers must include 'Host'")

        canonical_uri = self._canonical_uri(uri)
        canonical_query = self._canonical_query(query)  # type: ignore[arg-type]
        canonical_headers, signed_headers = self._canonical_headers(headers)

        canonical_request = "\n".join(
            [
                method,
                canonical_uri,
                canonical_query,
                canonical_headers,
                signed_headers,
                payload_hash,
            ]
        )
        return canonical_request.encode("utf-8")

    async def sign_envelope(
        self,
        key: KeyRef,
        env: Envelope,
        *,
        alg: Optional[Alg] = None,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        """Compute SigV4 Authorization over an HTTP request envelope."""

        akid, secret_key, _ = self._get_key_fields(key)
        amz_date = str(env.get("amz_date") or "")
        if not amz_date:
            amz_date = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

        date, region, service, scope = self._ensure_scope(env["scope"])
        canonical_request = (await self.canonicalize_envelope(env)).decode("utf-8")

        string_to_sign = self._string_to_sign(amz_date, scope, canonical_request)
        signing_key = self._derive_signing_key(secret_key, date, region, service)
        signature_hex = hmac.new(
            signing_key, string_to_sign.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        _, signed_headers = self._canonical_headers(env.get("headers") or {})

        signature: Signature = {
            "alg": "AWS4-HMAC-SHA256",
            "kid": akid,
            "amz_date": amz_date,
            "scope": scope,
            "signed_headers": signed_headers,
            "signature": signature_hex,
            "canonical_request_sha256": hashlib.sha256(
                canonical_request.encode("utf-8")
            ).hexdigest(),
        }
        return [signature]

    async def verify_envelope(
        self,
        env: Envelope,
        signatures: Sequence[Signature],
        *,
        canon: Optional[Canon] = None,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        """Recompute SigV4 and compare with provided signature(s)."""

        if not signatures:
            return False
        signature = signatures[0]
        amz_date = signature.get("amz_date") or env.get("amz_date")
        scope_str = signature.get("scope")
        if not amz_date or not scope_str:
            return False

        try:
            parts = scope_str.split("/")
            scope = {"date": parts[0], "region": parts[1], "service": parts[2]}
            date, region, service, _ = self._ensure_scope(scope)
        except Exception:
            return False

        secret = None
        if opts and "secret_key" in opts:
            secret = str(opts["secret_key"])
        elif require and "secret_key" in require:
            secret = str(require["secret_key"])
        if not secret:
            return False

        canonical_request = (await self.canonicalize_envelope(env)).decode("utf-8")
        string_to_sign = self._string_to_sign(
            str(amz_date), scope_str, canonical_request
        )
        signing_key = self._derive_signing_key(secret, date, region, service)
        calculated = hmac.new(
            signing_key, string_to_sign.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(calculated, str(signature.get("signature", "")))

    # ---------- payload-only (bytes) ----------
    async def sign_bytes(
        self,
        key: KeyRef,
        payload: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        """HMAC over raw bytes using a SigV4-derived signing key."""

        akid, secret_key, _ = self._get_key_fields(key)
        if not opts:
            raise ValueError("opts must include {date, region, service}")
        date = str(opts.get("date") or "")
        region = str(opts.get("region") or "")
        service = str(opts.get("service") or "")
        if not (date and region and service):
            raise ValueError("opts must include {date, region, service}")

        signing_key = self._derive_signing_key(secret_key, date, region, service)
        signature_hex = hmac.new(signing_key, payload, hashlib.sha256).hexdigest()
        signature: Signature = {
            "alg": "AWS4-HMAC-SHA256",
            "kid": akid,
            "scope": f"{date}/{region}/{service}/aws4_request",
            "signature": signature_hex,
        }
        return [signature]

    async def verify_bytes(
        self,
        payload: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        """Verify bytes HMAC using SigV4-derived key."""

        if not signatures:
            return False
        signature = signatures[0]
        scope_str = signature.get("scope") or ""
        parts = scope_str.split("/") if scope_str else []
        if len(parts) >= 4:
            date, region, service = parts[0], parts[1], parts[2]
        else:
            if not opts:
                return False
            date = str(opts.get("date") or "")
            region = str(opts.get("region") or "")
            service = str(opts.get("service") or "")
            if not (date and region and service):
                return False

        secret = None
        if require and "secret_key" in require:
            secret = str(require["secret_key"])
        elif opts and "secret_key" in opts:
            secret = str(opts["secret_key"])
        if not secret:
            return False

        signing_key = self._derive_signing_key(secret, date, region, service)
        calculated = hmac.new(signing_key, payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(calculated, str(signature.get("signature", "")))
