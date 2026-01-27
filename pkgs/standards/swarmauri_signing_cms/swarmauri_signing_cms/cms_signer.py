"""Cryptographic Message Syntax (CMS) SigningBase implementation."""

from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import (
    Any,
    AsyncIterable,
    Iterable,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Tuple,
)

from swarmauri_base import register_type
from swarmauri_base.signing.SigningBase import SigningBase
from swarmauri_core.crypto.types import Alg, KeyRef
from swarmauri_core.key_providers.IKeyProvider import IKeyProvider
from swarmauri_core.signing.ISigning import Canon, Envelope, StreamLike
from swarmauri_core.signing.types import Signature


class _PKCS7SignedDataShim:
    def __init__(self, artifact: bytes) -> None:
        self._artifact = artifact

    def verify(
        self,
        _certs: object | None,
        _trusted: object | None,
        *,
        data: bytes | None,
        options: list[object],
    ) -> None:
        return None


try:  # pragma: no cover - optional dependency
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.serialization import pkcs7
    from cryptography.hazmat.primitives.serialization.pkcs12 import (
        load_key_and_certificates,
    )

    if not hasattr(pkcs7, "load_der_pkcs7_signed_data"):

        def _load_der_pkcs7_signed_data(data: bytes) -> _PKCS7SignedDataShim:
            return _PKCS7SignedDataShim(data)

        setattr(pkcs7, "load_der_pkcs7_signed_data", _load_der_pkcs7_signed_data)

    if not hasattr(pkcs7, "load_pem_pkcs7_signed_data"):

        def _load_pem_pkcs7_signed_data(data: bytes) -> _PKCS7SignedDataShim:
            return _PKCS7SignedDataShim(data)

        setattr(pkcs7, "load_pem_pkcs7_signed_data", _load_pem_pkcs7_signed_data)

    _CRYPTO_OK = True
    _HAS_PKCS7_SIGNED_LOADER = hasattr(pkcs7, "load_der_pkcs7_signed_data")
except Exception:  # pragma: no cover - runtime check
    _CRYPTO_OK = False
    _HAS_PKCS7_SIGNED_LOADER = False


def _ensure_crypto() -> None:
    if not _CRYPTO_OK:
        raise RuntimeError(
            "CMSSigner requires the 'cryptography' package. Install with: pip install cryptography"
        )


def _canon_json(obj: Any) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


async def _stream_to_bytes(stream: StreamLike) -> bytes:
    if isinstance(stream, (bytes, bytearray)):
        return bytes(stream)
    if isinstance(stream, AsyncIterable):
        parts = [bytes(chunk) async for chunk in stream]
        return b"".join(parts)
    if isinstance(stream, Iterable):
        return b"".join(bytes(chunk) for chunk in stream)
    raise TypeError("Unsupported stream payload for CMS signing")


def _hash_from_alg(alg: Optional[Alg]) -> hashes.HashAlgorithm:
    if alg is None:
        return hashes.SHA256()
    normalized = str(alg).replace("-", "").replace("_", "").upper()
    mapping = {
        "SHA256": hashes.SHA256,
        "SHA384": hashes.SHA384,
        "SHA512": hashes.SHA512,
        "SHA1": hashes.SHA1,
    }
    if normalized not in mapping:
        raise ValueError(f"Unsupported CMS hash algorithm: {alg}")
    return mapping[normalized]()


def _load_pem(path_or_bytes: Any) -> bytes:
    if isinstance(path_or_bytes, bytes):
        return path_or_bytes
    if isinstance(path_or_bytes, str):
        path = Path(path_or_bytes)
        if path.exists():
            return path.read_bytes()
        return path_or_bytes.encode("utf-8")
    raise TypeError("Certificate/key entries must be bytes or filesystem paths")


def _load_signing_material(
    key_ref: KeyRef,
) -> Tuple[object, x509.Certificate, Sequence[x509.Certificate]]:
    _ensure_crypto()
    if isinstance(key_ref, Mapping):
        kind = key_ref.get("kind")
        if kind == "pem":
            priv = _load_pem(key_ref.get("private_key"))
            password = key_ref.get("password")
            password_bytes = None if password is None else str(password).encode("utf-8")
            private_key = serialization.load_pem_private_key(
                priv, password=password_bytes
            )
            cert_bytes = _load_pem(key_ref.get("certificate"))
            cert = x509.load_pem_x509_certificate(cert_bytes)
            extras: list[x509.Certificate] = []
            for entry in key_ref.get("extra_certificates", []) or []:
                extras.append(x509.load_pem_x509_certificate(_load_pem(entry)))
            return private_key, cert, extras
        if kind == "pkcs12":
            data = _load_pem(key_ref.get("data"))
            password = key_ref.get("password")
            password_bytes = None if password is None else str(password).encode("utf-8")
            private_key, cert, extra = load_key_and_certificates(data, password_bytes)
            if private_key is None or cert is None:
                raise RuntimeError(
                    "PKCS#12 bundle did not include both key and certificate"
                )
            extras = list(extra or [])
            return private_key, cert, extras
    raise TypeError("CMS KeyRef must describe 'pem' or 'pkcs12' material")


def _load_certificates(entries: Optional[Iterable[Any]]) -> list[x509.Certificate]:
    _ensure_crypto()
    certs: list[x509.Certificate] = []
    for entry in entries or []:
        certs.append(x509.load_pem_x509_certificate(_load_pem(entry)))
    return certs


def _serialize_signature(
    artifact: bytes,
    *,
    payload_kind: str,
    attached: bool,
    cert: x509.Certificate,
    extras: Sequence[x509.Certificate],
    hash_alg: hashes.HashAlgorithm,
) -> Signature:
    chain = [cert.public_bytes(serialization.Encoding.DER)] + [
        extra.public_bytes(serialization.Encoding.DER) for extra in extras
    ]
    fingerprint = cert.fingerprint(hashes.SHA256()).hex()
    meta: MutableMapping[str, Any] = {
        "payload_kind": payload_kind,
        "attached": attached,
    }
    return Signature(
        kid=fingerprint,
        version=None,
        format="cms",
        mode="attached" if attached else "detached",
        alg=hash_alg.name,
        artifact=artifact,
        cert_chain_der=tuple(chain),
        meta=meta,
    )


def _load_pkcs7(data: bytes) -> pkcs7.PKCS7Signature:
    _ensure_crypto()
    if not _HAS_PKCS7_SIGNED_LOADER:
        raise RuntimeError("cryptography does not expose PKCS7 signed data loaders")
    try:
        return pkcs7.load_der_pkcs7_signed_data(data)
    except ValueError:
        return pkcs7.load_pem_pkcs7_signed_data(data)


def _is_pem_signature(data: bytes) -> bool:
    return data.lstrip().startswith(b"-----BEGIN")


def _serialize_certs(certs: list[x509.Certificate]) -> bytes:
    return b"".join(cert.public_bytes(serialization.Encoding.PEM) for cert in certs)


def _openssl_verify(
    payload: bytes,
    artifact: bytes,
    *,
    attached: bool,
    trusted: list[x509.Certificate],
) -> bool:
    if not trusted:
        return False
    openssl_bin = shutil.which("openssl")
    if not openssl_bin:
        raise RuntimeError("OpenSSL binary is required for CMS verification")
    fmt = "pem" if _is_pem_signature(artifact) else "der"
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        sig_path = tmp_path / ("signature.pem" if fmt == "pem" else "signature.der")
        sig_path.write_bytes(artifact)
        trust_path = tmp_path / "trust.pem"
        trust_path.write_bytes(_serialize_certs(trusted))
        cmd = [
            openssl_bin,
            "smime",
            "-verify",
            "-inform",
            fmt,
            "-in",
            str(sig_path),
            "-CAfile",
            str(trust_path),
        ]
        if not attached:
            data_path = tmp_path / "payload.bin"
            data_path.write_bytes(payload)
            cmd.extend(["-content", str(data_path)])
        proc = subprocess.run(cmd, capture_output=True)
        if proc.returncode != 0:
            return False
        if attached:
            return proc.stdout == payload
        return True


async def _verify_pkcs7(
    payload: bytes,
    artifact: bytes,
    *,
    attached: bool,
    trusted: list[x509.Certificate],
) -> bool:
    if _HAS_PKCS7_SIGNED_LOADER:
        signed = _load_pkcs7(artifact)
        options = [] if attached else [pkcs7.PKCS7Options.DetachedSignature]
        data = None if attached else payload
        if isinstance(signed, _PKCS7SignedDataShim):
            return await asyncio.to_thread(
                _openssl_verify,
                payload,
                artifact,
                attached=attached,
                trusted=trusted,
            )
        signed.verify(trusted or None, trusted or None, data=data, options=options)
        return True
    return await asyncio.to_thread(
        _openssl_verify,
        payload,
        artifact,
        attached=attached,
        trusted=trusted,
    )


def _min_signers(require: Optional[Mapping[str, object]]) -> int:
    if not require:
        return 1
    try:
        return max(1, int(require.get("min_signers", 1)))
    except (TypeError, ValueError):
        return 1


@register_type(resource_type=SigningBase)
class CMSSigner(SigningBase):
    """Create PKCS#7/CMS detached or attached signatures."""

    def __init__(
        self,
        key_provider: Optional[IKeyProvider] = None,
    ) -> None:
        self._key_provider = key_provider

    def set_key_provider(self, provider: IKeyProvider) -> None:
        self._key_provider = provider

    # ------------------------------------------------------------------
    def supports(self, key_ref: Optional[str] = None) -> Mapping[str, Iterable[str]]:
        base = {
            "signs": ("bytes", "digest", "envelope", "stream"),
            "verifies": ("bytes", "digest", "envelope", "stream"),
            "envelopes": ("structured-json", "detached-bytes"),
            "algs": ("SHA256", "SHA384", "SHA512", "SHA1"),
            "canons": ("json",),
            "features": ("attached", "detached", "pkcs7"),
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
        return await type(self)._sign_payload(
            key,
            payload,
            alg=alg,
            opts=opts,
            payload_kind="bytes",
        )

    async def sign_digest(
        self,
        key: KeyRef,
        digest: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        return await type(self)._sign_payload(
            key,
            digest,
            alg=alg,
            opts=opts,
            payload_kind="digest",
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
        return await type(self)._sign_payload(
            key,
            data,
            alg=alg,
            opts=opts,
            payload_kind="stream",
        )

    async def sign_envelope(
        self,
        key: KeyRef,
        env: Envelope,
        *,
        alg: Optional[Alg] = None,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        canonical = await type(self).canonicalize_envelope(env, canon=canon, opts=opts)
        return await type(self)._sign_payload(
            key,
            canonical,
            alg=alg,
            opts=opts,
            payload_kind="envelope",
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
        return await type(self)._verify_payload(
            payload,
            signatures,
            require=require,
            opts=opts,
            payload_kind="bytes",
        )

    async def verify_digest(
        self,
        digest: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        return await type(self)._verify_payload(
            digest,
            signatures,
            require=require,
            opts=opts,
            payload_kind="digest",
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
        return await type(self)._verify_payload(
            data,
            signatures,
            require=require,
            opts=opts,
            payload_kind="stream",
        )

    async def verify_envelope(
        self,
        env: Envelope,
        signatures: Sequence[Signature],
        *,
        canon: Optional[Canon] = None,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        canonical = await type(self).canonicalize_envelope(env, canon=canon, opts=opts)
        return await type(self)._verify_payload(
            canonical,
            signatures,
            require=require,
            opts=opts,
            payload_kind="envelope",
        )

    # ------------------------------------------------------------------
    @staticmethod
    async def canonicalize_envelope(
        env: Envelope,
        *,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        if canon in (None, "json"):
            return _canon_json(env)
        if canon == "raw":
            if isinstance(env, (bytes, bytearray)):
                return bytes(env)
            raise TypeError("raw canon expects bytes envelope")
        raise ValueError(f"Unsupported canon for CMSSigner: {canon}")

    # ------------------------------------------------------------------
    @staticmethod
    async def _sign_payload(
        key: KeyRef,
        payload: bytes,
        *,
        alg: Optional[Alg],
        opts: Optional[Mapping[str, object]],
        payload_kind: str,
    ) -> Sequence[Signature]:
        private_key, cert, extras = _load_signing_material(key)
        hash_alg = _hash_from_alg(alg or (opts or {}).get("hash_alg"))
        builder = pkcs7.PKCS7SignatureBuilder().set_data(payload)
        builder = builder.add_signer(cert, private_key, hash_alg)
        for extra in extras:
            builder = builder.add_certificate(extra)
        attached = bool((opts or {}).get("attached", False))
        encoding = str((opts or {}).get("encoding", "der")).lower()
        if encoding == "pem":
            enc = serialization.Encoding.PEM
        elif encoding == "der":
            enc = serialization.Encoding.DER
        else:
            raise ValueError("encoding must be 'der' or 'pem'")
        options = [] if attached else [pkcs7.PKCS7Options.DetachedSignature]
        artifact = builder.sign(enc, options)
        return [
            _serialize_signature(
                artifact,
                payload_kind=payload_kind,
                attached=attached,
                cert=cert,
                extras=extras,
                hash_alg=hash_alg,
            )
        ]

    @staticmethod
    async def _verify_payload(
        payload: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]],
        opts: Optional[Mapping[str, object]],
        payload_kind: str,
    ) -> bool:
        if not signatures:
            return False
        trusted = _load_certificates((opts or {}).get("trusted_certs"))
        min_ok = _min_signers(require)
        accepted = 0
        for sig in signatures:
            meta = sig.meta if isinstance(sig, Signature) else sig.get("meta")
            kind = meta.get("payload_kind") if isinstance(meta, Mapping) else None
            if kind not in (None, payload_kind):
                continue
            artifact = (
                sig.artifact if isinstance(sig, Signature) else sig.get("artifact")
            )
            if isinstance(artifact, str):
                artifact_bytes = artifact.encode("utf-8")
            elif isinstance(artifact, (bytes, bytearray)):
                artifact_bytes = bytes(artifact)
            else:
                continue
            attached = (
                bool(meta.get("attached")) if isinstance(meta, Mapping) else False
            )
            try:
                ok = await _verify_pkcs7(
                    payload,
                    artifact_bytes,
                    attached=attached,
                    trusted=trusted,
                )
            except Exception:
                continue
            if ok:
                accepted += 1
                if accepted >= min_ok:
                    return True
        return False
