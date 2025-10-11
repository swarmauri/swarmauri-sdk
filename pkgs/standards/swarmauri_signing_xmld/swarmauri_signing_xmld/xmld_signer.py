"""XML Digital Signature provider."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, AsyncIterable, Iterable, Mapping, Optional, Sequence

from swarmauri_base import register_type
from swarmauri_base.signing.SigningBase import SigningBase
from swarmauri_core.crypto.types import Alg, KeyRef
from swarmauri_core.key_providers.IKeyProvider import IKeyProvider
from swarmauri_core.signing.ISigning import Canon, Envelope, StreamLike
from swarmauri_core.signing.types import Signature

try:  # pragma: no cover - runtime guards
    from lxml import etree

    _LXML_OK = True
except Exception:  # pragma: no cover
    _LXML_OK = False

try:  # pragma: no cover - runtime guards
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec, ed25519, padding, rsa

    _CRYPTO_OK = True
except Exception:  # pragma: no cover
    _CRYPTO_OK = False


def _ensure_deps() -> None:
    if not _LXML_OK:
        raise RuntimeError("XMLDSigner requires 'lxml'. Install with: pip install lxml")
    if not _CRYPTO_OK:
        raise RuntimeError(
            "XMLDSigner requires 'cryptography'. Install with: pip install cryptography"
        )


async def _stream_to_bytes(stream: StreamLike) -> bytes:
    if isinstance(stream, (bytes, bytearray)):
        return bytes(stream)
    if isinstance(stream, AsyncIterable):
        parts = [bytes(chunk) async for chunk in stream]
        return b"".join(parts)
    if isinstance(stream, Iterable):
        return b"".join(bytes(chunk) for chunk in stream)
    raise TypeError("Unsupported stream payload for XMLDSigner")


def _canon_xml(
    data: Any, *, canon: str = "c14n", inclusive_ns: Optional[Sequence[str]] = None
) -> bytes:
    _ensure_deps()
    if isinstance(data, (bytes, bytearray)):
        document = etree.fromstring(bytes(data))
    elif isinstance(data, str):
        document = etree.fromstring(data.encode("utf-8"))
    else:
        raise TypeError("XML canonicalization expects bytes or str input")
    if canon in (None, "c14n"):
        return etree.tostring(
            document,
            method="c14n",
            exclusive=False,
            with_comments=False,
            inclusive_ns_prefixes=inclusive_ns,
        )
    if canon == "c14n11":
        return etree.tostring(
            document,
            method="c14n",
            exclusive=False,
            with_comments=False,
            c14n_version=1.1,
        )
    if canon == "exc-c14n":
        return etree.tostring(
            document,
            method="c14n",
            exclusive=True,
            with_comments=False,
            inclusive_ns_prefixes=inclusive_ns,
        )
    raise ValueError(f"Unsupported XML canon '{canon}'")


def _load_pem(entry: Any) -> bytes:
    if isinstance(entry, bytes):
        return entry
    if isinstance(entry, str):
        path = Path(entry)
        if path.exists():
            return path.read_bytes()
        return entry.encode("utf-8")
    raise TypeError("PEM entries must be bytes or filesystem paths")


def _load_private_key(key_ref: KeyRef):
    _ensure_deps()
    if isinstance(key_ref, Mapping):
        kind = key_ref.get("kind")
        password = key_ref.get("password")
        password_bytes = None if password is None else str(password).encode("utf-8")
        if kind == "pem":
            pem = _load_pem(key_ref.get("private_key"))
            return serialization.load_pem_private_key(pem, password=password_bytes)
        if kind == "pkcs12":
            data = _load_pem(key_ref.get("data"))
            from cryptography.hazmat.primitives.serialization.pkcs12 import (
                load_key_and_certificates,
            )

            private_key, cert, extras = load_key_and_certificates(data, password_bytes)
            if private_key is None:
                raise RuntimeError("PKCS#12 bundle did not include a private key")
            return private_key
    raise TypeError("XMLDSigner key_ref must describe 'pem' or 'pkcs12' material")


def _load_certificate(key_ref: KeyRef) -> Optional[x509.Certificate]:
    if isinstance(key_ref, Mapping):
        cert_entry = key_ref.get("certificate")
        if cert_entry is None:
            return None
        return x509.load_pem_x509_certificate(_load_pem(cert_entry))
    return None


def _fingerprint(public_bytes: bytes) -> str:
    return hashlib.sha256(public_bytes).hexdigest()


def _resolve_alg(
    key, alg: Optional[Alg]
) -> tuple[str, Any, hashes.HashAlgorithm | None]:
    normalized = str(alg).upper() if alg else None
    if isinstance(key, rsa.RSAPrivateKey):
        hash_alg = hashes.SHA256()
        mode = padding.PSS(
            mgf=padding.MGF1(hash_alg), salt_length=padding.PSS.MAX_LENGTH
        )
        name = "RSA-PSS-SHA256"
        if normalized and "PKCS1" in normalized:
            mode = padding.PKCS1v15()
            name = "RSA-PKCS1-SHA256"
        return name, mode, hash_alg
    if isinstance(key, ec.EllipticCurvePrivateKey):
        hash_alg = hashes.SHA256()
        return "ECDSA-SHA256", ec.ECDSA(hash_alg), hash_alg
    if isinstance(key, ed25519.Ed25519PrivateKey):
        return "Ed25519", None, None
    raise TypeError("Unsupported key type for XMLDSigner")


def _load_public_keys(entries: Optional[Iterable[Any]]) -> list[Any]:
    _ensure_deps()
    keys: list[Any] = []
    for entry in entries or []:
        if isinstance(
            entry,
            (rsa.RSAPublicKey, ec.EllipticCurvePublicKey, ed25519.Ed25519PublicKey),
        ):
            keys.append(entry)
            continue
        pem = _load_pem(entry)
        try:
            keys.append(serialization.load_pem_public_key(pem))
            continue
        except ValueError:
            cert = x509.load_pem_x509_certificate(pem)
            keys.append(cert.public_key())
    return keys


def _serialize_signature(
    sig: bytes,
    *,
    payload_kind: str,
    alg_name: str,
    canon: str,
    cert: Optional[x509.Certificate],
) -> Signature:
    kid = None
    if cert is not None:
        kid = _fingerprint(cert.public_bytes(serialization.Encoding.DER))
    meta = {"payload_kind": payload_kind, "canon": canon}
    cert_chain = None
    if cert is not None:
        cert_chain = (cert.public_bytes(serialization.Encoding.DER),)
    return Signature(
        kid=kid,
        version=None,
        format="xml-dsig",
        mode="detached",
        alg=alg_name,
        artifact=sig,
        cert_chain_der=cert_chain,
        meta=meta,
    )


def _min_signers(require: Optional[Mapping[str, object]]) -> int:
    if not require:
        return 1
    try:
        return max(1, int(require.get("min_signers", 1)))
    except (TypeError, ValueError):
        return 1


@register_type(resource_type=SigningBase)
class XMLDSigner(SigningBase):
    """Produce detached XML Digital Signatures over canonicalized payloads."""

    def __init__(self, key_provider: Optional[IKeyProvider] = None) -> None:
        self._key_provider = key_provider

    def set_key_provider(self, provider: IKeyProvider) -> None:
        self._key_provider = provider

    # ------------------------------------------------------------------
    def supports(self, key_ref: Optional[str] = None) -> Mapping[str, Iterable[str]]:
        base = {
            "signs": ("bytes", "digest", "envelope", "stream"),
            "verifies": ("bytes", "digest", "envelope", "stream"),
            "envelopes": ("xml", "structured-json"),
            "algs": ("RSA-PSS-SHA256", "RSA-PKCS1-SHA256", "ECDSA-SHA256", "Ed25519"),
            "canons": ("c14n", "c14n11", "exc-c14n"),
            "features": ("detached", "xml-dsig"),
            "status": ("beta",),
        }
        if key_ref is None:
            return base
        return {**base, "key_refs": (key_ref,)}

    # ------------------------------------------------------------------
    async def sign_bytes(
        self,
        key: KeyRef,
        payload: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        return await self._sign_payload(
            key,
            payload,
            alg=alg,
            opts=opts,
            payload_kind="bytes",
            canon="raw",
        )

    async def sign_digest(
        self,
        key: KeyRef,
        digest: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        return await self._sign_payload(
            key,
            digest,
            alg=alg,
            opts=opts,
            payload_kind="digest",
            canon="raw",
        )

    async def sign_stream(
        self,
        key: KeyRef,
        payload: StreamLike,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        data = await _stream_to_bytes(payload)
        return await self.sign_bytes(key, data, alg=alg, opts=opts)

    async def sign_envelope(
        self,
        key: KeyRef,
        env: Envelope,
        *,
        alg: Optional[Alg] = None,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        canonical = await self.canonicalize_envelope(env, canon=canon, opts=opts)
        return await self._sign_payload(
            key,
            canonical,
            alg=alg,
            opts=opts,
            payload_kind="envelope",
            canon=str(canon or "c14n"),
        )

    # ------------------------------------------------------------------
    async def verify_bytes(
        self,
        payload: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        return await self._verify_payload(
            payload,
            signatures,
            require=require,
            opts=opts,
            payload_kind="bytes",
            canon="raw",
        )

    async def verify_digest(
        self,
        digest: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        return await self._verify_payload(
            digest,
            signatures,
            require=require,
            opts=opts,
            payload_kind="digest",
            canon="raw",
        )

    async def verify_stream(
        self,
        payload: StreamLike,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        data = await _stream_to_bytes(payload)
        return await self.verify_bytes(data, signatures, require=require, opts=opts)

    async def verify_envelope(
        self,
        env: Envelope,
        signatures: Sequence[Signature],
        *,
        canon: Optional[Canon] = None,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        canonical = await self.canonicalize_envelope(env, canon=canon, opts=opts)
        return await self._verify_payload(
            canonical,
            signatures,
            require=require,
            opts=opts,
            payload_kind="envelope",
            canon=str(canon or "c14n"),
        )

    # ------------------------------------------------------------------
    async def canonicalize_envelope(
        self,
        env: Envelope,
        *,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        token = canon or "c14n"
        if token == "raw":
            if isinstance(env, (bytes, bytearray)):
                return bytes(env)
            if isinstance(env, str):
                return env.encode("utf-8")
            raise TypeError("raw canon expects bytes or str")
        return _canon_xml(env, canon=str(token))

    # ------------------------------------------------------------------
    async def _sign_payload(
        self,
        key: KeyRef,
        payload: bytes,
        *,
        alg: Optional[Alg],
        opts: Optional[Mapping[str, object]],
        payload_kind: str,
        canon: str,
    ) -> Sequence[Signature]:
        private_key = _load_private_key(key)
        cert = _load_certificate(key)
        alg_name, mode, hash_alg = _resolve_alg(private_key, alg)
        data = payload
        if payload_kind == "envelope" and canon != "raw":
            data = payload  # already canonicalized
        if isinstance(private_key, ed25519.Ed25519PrivateKey):
            sig = private_key.sign(data)
        elif isinstance(private_key, ec.EllipticCurvePrivateKey):
            sig = private_key.sign(data, mode)  # type: ignore[arg-type]
        else:
            sig = private_key.sign(data, mode, hash_alg)  # type: ignore[arg-type]
        return [
            _serialize_signature(
                sig,
                payload_kind=payload_kind,
                alg_name=alg_name,
                canon=canon,
                cert=cert,
            )
        ]

    async def _verify_payload(
        self,
        payload: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]],
        opts: Optional[Mapping[str, object]],
        payload_kind: str,
        canon: str,
    ) -> bool:
        if not signatures:
            return False
        keys = _load_public_keys((opts or {}).get("pubkeys"))
        if not keys:
            raise RuntimeError(
                "XMLDSigner verification requires opts['pubkeys'] entries"
            )
        min_ok = _min_signers(require)
        accepted = 0
        for sig in signatures:
            meta = sig.meta if isinstance(sig, Signature) else sig.get("meta")
            kind = meta.get("payload_kind") if isinstance(meta, Mapping) else None
            if kind not in (None, payload_kind):
                continue
            canon_token = meta.get("canon") if isinstance(meta, Mapping) else canon
            if payload_kind == "envelope" and canon_token != canon:
                continue
            artifact = (
                sig.artifact if isinstance(sig, Signature) else sig.get("artifact")
            )
            if isinstance(artifact, str):
                signature_bytes = artifact.encode("utf-8")
            elif isinstance(artifact, (bytes, bytearray)):
                signature_bytes = bytes(artifact)
            else:
                continue
            alg_name = sig.alg if isinstance(sig, Signature) else sig.get("alg")
            for key in keys:
                try:
                    if isinstance(key, rsa.RSAPublicKey):
                        mode = padding.PSS(
                            mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=padding.PSS.MAX_LENGTH,
                        )
                        if alg_name and "PKCS1" in str(alg_name).upper():
                            mode = padding.PKCS1v15()
                        key.verify(signature_bytes, payload, mode, hashes.SHA256())
                        accepted += 1
                        break
                    if isinstance(key, ec.EllipticCurvePublicKey):
                        key.verify(signature_bytes, payload, ec.ECDSA(hashes.SHA256()))
                        accepted += 1
                        break
                    if isinstance(key, ed25519.Ed25519PublicKey):
                        key.verify(signature_bytes, payload)
                        accepted += 1
                        break
                except Exception:
                    continue
            if accepted >= min_ok:
                return True
        return False
