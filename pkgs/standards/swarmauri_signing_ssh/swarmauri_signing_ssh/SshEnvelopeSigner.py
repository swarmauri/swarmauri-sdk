"""
OpenSSH-based signing utilities.

This module wraps the ``ssh-keygen -Y`` command to create and verify
``sshsig`` signatures for raw byte payloads or structured envelopes.
It also provides helpers for canonicalizing envelopes using JSON or
optional CBOR canonicalization when ``cbor2`` is installed.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional, Sequence, Tuple

from swarmauri_base.signing.SigningBase import SigningBase
from swarmauri_core.signing.ISigning import Signature, Envelope, Canon
from swarmauri_core.crypto.types import KeyRef, Alg

try:  # pragma: no cover - optional canonicalization
    import cbor2

    _CBOR_OK = True
except Exception:  # pragma: no cover - runtime check
    _CBOR_OK = False


# ───────────────────────────── Helpers ─────────────────────────────


def _require_ssh_keygen() -> None:
    if shutil.which("ssh-keygen") is None:
        raise RuntimeError(
            "SshEnvelopeSigner requires OpenSSH 'ssh-keygen' on PATH (v8.2+ with -Y support)."
        )


def _canon_json(obj: Any) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _canon_cbor(obj: Any) -> bytes:
    if not _CBOR_OK:
        raise RuntimeError(
            "CBOR canonicalization requires 'cbor2'. Install with: pip install cbor2"
        )
    return cbor2.dumps(obj)


def _ensure_bytes(v: Any, *, name: str) -> bytes:
    if isinstance(v, (bytes, bytearray)):
        return bytes(v)
    if isinstance(v, str):
        return v.encode("utf-8")
    raise TypeError(f"{name} must be bytes or str")


def _write_temp(prefix: str, data: bytes, mode: int = 0o600) -> str:
    fd, path = tempfile.mkstemp(prefix=prefix)
    try:
        os.write(fd, data)
    finally:
        os.close(fd)
    os.chmod(path, mode)
    return path


def _read_file(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def _run(
    cmd: list[str], *, stdin: Optional[bytes] = None, check: bool = True
) -> Tuple[int, bytes, bytes]:
    p = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE if stdin is not None else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = p.communicate(stdin)
    if check and p.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}\n{err.decode('utf-8', 'ignore')}"
        )
    return p.returncode, out or b"", err or b""


def _pub_from_priv_path(priv_path: str) -> str:
    _, out, _ = _run(["ssh-keygen", "-y", "-f", priv_path], check=True)
    return out.decode("utf-8").strip()


def _fingerprint_from_publine(pub_line: str) -> str:
    path = _write_temp("ssh_pub_", _ensure_bytes(pub_line, name="pub"))
    try:
        _, out, _ = _run(["ssh-keygen", "-lf", path], check=True)
        text = out.decode("utf-8").strip()
        parts = text.split()
        for p in parts:
            if p.startswith("SHA256:"):
                return p
        return text
    finally:
        os.remove(path)


def _keytype_from_publine(pub_line: str) -> str:
    return pub_line.split()[0]


def _alg_token_from_keytype(keytype: str, hashalg: Optional[str]) -> str:
    if keytype == "ssh-ed25519":
        return "ssh-ed25519"
    if keytype == "ssh-rsa":
        return f"rsa-sha2-{hashalg or '256'}"
    if keytype.startswith("ecdsa-sha2-"):
        return keytype
    return keytype


def _allowed_signers_content(identity: str, pub_line: str) -> bytes:
    return f"{identity} {pub_line}\n".encode("utf-8")


# ───────────────────────────── KeyRef handling ─────────────────────────────


def _resolve_privkey_to_path(key: KeyRef) -> Tuple[str, str, str]:
    if not isinstance(key, dict):
        raise TypeError("SSH KeyRef must be a dict.")
    kind = key.get("kind")
    identity = key.get("identity") or "default"
    if kind == "path":
        priv_path = str(key.get("priv"))
        if not os.path.exists(priv_path):
            raise FileNotFoundError(f"Private key file not found: {priv_path}")
        pub_line = _pub_from_priv_path(priv_path)
        return priv_path, str(identity), _keytype_from_publine(pub_line)
    if kind == "pem":
        data = _ensure_bytes(key.get("priv"), name="priv")
        tmp = _write_temp("ssh_priv_", data, mode=0o600)
        pub_line = _pub_from_priv_path(tmp)
        return tmp, str(identity), _keytype_from_publine(pub_line)
    raise TypeError(f"Unsupported KeyRef kind for SSH signing: {kind}")


def _extract_pub_from_priv(priv_path: str) -> str:
    return _pub_from_priv_path(priv_path)


# ───────────────────────────── Signature container ─────────────────────────────


@dataclass(frozen=True)
class _Sig:
    data: dict[str, Any]

    def get(self, k: str, default=None):
        return self.data.get(k, default)

    def __getitem__(self, k: str) -> object:
        return self.data[k]

    def __iter__(self):
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)


# ───────────────────────────── Signer ─────────────────────────────


class SshEnvelopeSigner(SigningBase):
    """
    Create and verify OpenSSH detached signatures.

    This signer invokes ``ssh-keygen -Y`` to produce and validate ``sshsig``
    signatures for raw byte payloads or canonicalized envelopes.
    """

    def supports(self) -> Mapping[str, Iterable[str]]:
        """Declare supported algorithms and canonicalization formats."""

        canons = ("json", "cbor") if _CBOR_OK else ("json",)
        envelopes = ("detached-bytes", "ssh-signed-envelope") + tuple(
            f"structured-{canon}" for canon in canons
        )
        algs = (
            "ssh-ed25519",
            "ssh-rsa",
            "rsa-sha2-256",
            "rsa-sha2-512",
            "ecdsa-sha2-nistp256",
            "ecdsa-sha2-nistp384",
            "ecdsa-sha2-nistp521",
        )
        return {
            "algs": algs,
            "canons": canons,
            "signs": ("bytes", "digest", "envelope", "stream"),
            "verifies": ("bytes", "digest", "envelope", "stream"),
            "envelopes": ("mapping", *envelopes),
            "features": ("multi", "detached_only"),
        }

    async def sign_bytes(
        self,
        key: KeyRef,
        payload: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        """
        Sign a payload and return detached SSH signatures.

        Args:
            key (KeyRef): Reference to the private key used for signing.
            payload (bytes): Raw data to sign.
            alg (Optional[Alg]): Algorithm override. Defaults to ``None``.
            opts (Optional[Mapping[str, object]]): Extra options such as
                ``namespace`` or ``hashalg``. Defaults to ``None``.

        Returns:
            Sequence[Signature]: The generated signature collection.

        Raises:
            RuntimeError: If ``ssh-keygen`` is unavailable or signing fails.
            TypeError: If the key reference is invalid.
        """

        _require_ssh_keygen()

        priv_path, identity, keytype = _resolve_privkey_to_path(key)
        temp_key = None
        if isinstance(key, dict) and key.get("kind") == "pem":
            temp_key = priv_path

        namespace = str((opts or {}).get("namespace") or "file")
        hashalg = (
            (key.get("hashalg") if isinstance(key, dict) else None)
            or (opts or {}).get("hashalg")
            or ("sha256" if keytype == "ssh-rsa" else None)
        )
        pub_line = _extract_pub_from_priv(priv_path)
        kid = _fingerprint_from_publine(pub_line)
        alg_token = _alg_token_from_keytype(keytype, hashalg)

        cmd = ["ssh-keygen", "-Y", "sign", "-f", priv_path, "-n", namespace]
        if hashalg in ("sha256", "sha512"):
            cmd += ["-O", f"hashalg={hashalg}"]

        try:
            _, sig, _ = _run(cmd, stdin=payload, check=True)
            return [
                _Sig(
                    {
                        "alg": alg_token,
                        "kid": kid,
                        "sig": sig,
                        "format": "sshsig",
                        "namespace": namespace,
                        "identity": identity,
                        "keytype": keytype,
                    }
                )
            ]
        finally:
            if temp_key:
                try:
                    os.remove(temp_key)
                except Exception:  # pragma: no cover - cleanup best-effort
                    pass

    async def verify_bytes(
        self,
        payload: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        """
        Verify SSH signatures for a payload.

        Args:
            payload (bytes): Original message that was signed.
            signatures (Sequence[Signature]): Signatures to verify.
            require (Optional[Mapping[str, object]]): Verification constraints
                such as ``min_signers``, ``algs`` or ``kids``. Defaults to ``None``.
            opts (Optional[Mapping[str, object]]): Options including ``pubkeys``
                with a list of SSH public key lines and optional ``namespace`` or
                ``identity``. Defaults to ``None``.

        Returns:
            bool: ``True`` if verification succeeds, otherwise ``False``.

        Raises:
            RuntimeError: If required options are missing or verification fails.
            TypeError: If provided public keys or signatures are malformed.
        """

        _require_ssh_keygen()

        req = require or {}
        min_signers = int(req.get("min_signers", 1))
        allowed_algs = set(req.get("algs") or [])
        required_kids = set(req.get("kids") or [])

        namespace = str((opts or {}).get("namespace") or "file")
        identity_hint = (opts or {}).get("identity")
        pubkeys = (opts or {}).get("pubkeys") or []
        if not isinstance(pubkeys, (list, tuple)) or not pubkeys:
            raise RuntimeError(
                "SshEnvelopeSigner.verify_bytes requires opts['pubkeys'] with one or more SSH public keys."
            )

        allowed_lines = []
        for idx, key_entry in enumerate(pubkeys):
            if not isinstance(key_entry, str):
                raise TypeError(
                    "opts['pubkeys'] entries must be OpenSSH public key lines (str)."
                )
            identity = str(identity_hint or f"signer{idx}")
            allowed_lines.append(_allowed_signers_content(identity, key_entry))
        allowed_blob = b"".join(allowed_lines)
        allowed_path = _write_temp("ssh_allowed_", allowed_blob, mode=0o600)

        try:
            accepted = 0
            for sig in signatures:
                sig_bytes = sig.get("sig")
                if not isinstance(sig_bytes, (bytes, bytearray)):
                    continue
                keytype = str(sig.get("keytype") or "")
                if allowed_algs and (
                    sig.get("alg") not in allowed_algs and keytype not in allowed_algs
                ):
                    continue
                if required_kids:
                    kid = sig.get("kid")
                    if not isinstance(kid, str) or kid not in required_kids:
                        continue

                sig_path = _write_temp("ssh_sig_", bytes(sig_bytes), mode=0o600)
                try:
                    cmd = [
                        "ssh-keygen",
                        "-Y",
                        "verify",
                        "-f",
                        allowed_path,
                        "-I",
                        str(sig.get("identity") or identity_hint or "signer0"),
                        "-n",
                        str(sig.get("namespace") or namespace),
                        "-s",
                        sig_path,
                    ]
                    rc, _, _ = _run(cmd, stdin=payload, check=False)
                    if rc == 0:
                        accepted += 1
                        if accepted >= min_signers:
                            return True
                finally:
                    os.remove(sig_path)
            return False
        finally:
            os.remove(allowed_path)

    async def sign_digest(
        self,
        key: KeyRef,
        digest: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        return await self.sign_bytes(key, digest, alg=alg, opts=opts)

    async def verify_digest(
        self,
        digest: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        return await self.verify_bytes(digest, signatures, require=require, opts=opts)

    async def canonicalize_envelope(
        self,
        env: Envelope,
        *,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        """
        Serialize an envelope to a canonical byte representation.

        Args:
            env (Envelope): Envelope to canonicalize.
            canon (Optional[Canon]): Canonicalization format (``"json"`` or
                ``"cbor"``). Defaults to ``"json"``.
            opts (Optional[Mapping[str, object]]): Additional options. Defaults
                to ``None``.

        Returns:
            bytes: Canonicalized envelope bytes.

        Raises:
            ValueError: If the requested canonicalization format is unsupported.
        """

        if canon in (None, "json"):
            return _canon_json(env)  # type: ignore[arg-type]
        if canon == "cbor":
            return _canon_cbor(env)  # type: ignore[arg-type]
        raise ValueError(f"Unsupported canon: {canon}")

    async def sign_envelope(
        self,
        key: KeyRef,
        env: Envelope,
        *,
        alg: Optional[Alg] = None,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        """
        Sign a structured envelope.

        Args:
            key (KeyRef): Reference to the private key used for signing.
            env (Envelope): Envelope to sign.
            alg (Optional[Alg]): Algorithm override. Defaults to ``None``.
            canon (Optional[Canon]): Canonicalization format. Defaults to
                ``"json"``.
            opts (Optional[Mapping[str, object]]): Extra options forwarded to
                :meth:`sign_bytes`. Defaults to ``None``.

        Returns:
            Sequence[Signature]: The generated signature collection.
        """

        payload = await self.canonicalize_envelope(env, canon=canon, opts=opts)
        return await self.sign_bytes(key, payload, alg=alg, opts=opts)

    async def verify_envelope(
        self,
        env: Envelope,
        signatures: Sequence[Signature],
        *,
        canon: Optional[Canon] = None,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        """
        Verify signatures over a structured envelope.

        Args:
            env (Envelope): Envelope data to verify.
            signatures (Sequence[Signature]): Signatures to validate.
            canon (Optional[Canon]): Canonicalization format. Defaults to
                ``"json"``.
            require (Optional[Mapping[str, object]]): Verification constraints as
                described in :meth:`verify_bytes`. Defaults to ``None``.
            opts (Optional[Mapping[str, object]]): Extra options forwarded to
                :meth:`verify_bytes`. Defaults to ``None``.

        Returns:
            bool: ``True`` if verification succeeds, otherwise ``False``.
        """

        payload = await self.canonicalize_envelope(env, canon=canon, opts=opts)
        return await self.verify_bytes(payload, signatures, require=require, opts=opts)
