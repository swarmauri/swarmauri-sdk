"""
ISigning: Detached signing / verification interface (envelope‑agnostic).

Design goals
------------
- One interface that cleanly supports:
  • Signing/verification of raw bytes.
  • Signing/verification of pre-hashed digests.
  • Signing/verification of stream-friendly iterables of bytes.
  • Signing/verification of structured envelopes (AEAD or MRE) via canonicalization.
- No encryption here (kept in ICrypto/IMreCrypto).
- Multi‑signer friendly: return one or more detached signatures; verification
  can accept N signatures and enforce policy (e.g., m‑of‑n) at the caller.

Conventions
-----------
- "alg" describes the signature scheme (e.g., "Ed25519", "RSA-PSS-SHA256", "OpenPGP").
- Canonicalization MUST be deterministic. Implementations should document which
  canonical form(s) they support (e.g., JSON‑canonical, CBOR‑canonical).
- Key material is referenced via KeyRef (HSM handle, KMS id, in‑memory key, etc.).

Typical flows
-------------
- Bytes:
    sigs = await signer.sign_bytes(my_key, b"payload", alg="Ed25519")
    ok = await signer.verify_bytes(b"payload", sigs)

- Digest:
    digest = hashlib.sha256(b"payload").digest()
    sigs = await signer.sign_digest(my_key, digest, alg="Ed25519")
    ok = await signer.verify_digest(digest, sigs)

- Stream:
    sigs = await signer.sign_stream(my_key, payload_iter, alg="Ed25519")
    ok = await signer.verify_stream(payload_iter, sigs)

- Envelopes (AEAD or MRE):
    sigs = await signer.sign_envelope(my_key, env, alg="Ed25519", canon="json")
    ok = await signer.verify_envelope(env, sigs, canon="json")

Notes
-----
- This ABC is intentionally minimal. Providers may expose additional methods,
  but must implement the surface below.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterable, Iterable, Mapping, Optional, Sequence, Union

from ..crypto.types import Alg, KeyRef
from ..crypto.types import AEADCiphertext  # single‑recipient envelope
from ..mre_crypto.types import MultiRecipientEnvelope  # multi‑recipient envelope
from .types import Signature


# --------- Canonicalization tokens (stringly‑typed to avoid a hard dep) ---------
# Examples: "json", "json-c14n", "cbor", "dag-json", "raw" (no canonicalization)
Canon = str

Envelope = Union[AEADCiphertext, MultiRecipientEnvelope, Mapping[str, object]]
StreamLike = Union[Iterable[bytes], AsyncIterable[bytes]]


class ISigning(ABC):
    @abstractmethod
    def supports(self) -> Mapping[str, Iterable[str]]:
        """
        Return capability information.

        Keys (omit if unsupported):
          - "algs": iterable of signature algorithms (e.g., "Ed25519", "RSA-PSS-SHA256", "OpenPGP").
          - "canons": iterable of canonicalization identifiers (e.g., "json", "cbor", "json-c14n").
          - "features": optional iterable of flags, e.g.:
                • "multi"          → optimized for multi‑signature sets
                • "detached_only"  → only detached signatures (default)
                • "attest"         → can include attestation chains in Signature["chain"]
        """
        ...

    # ────────────────────────────────── Bytes ──────────────────────────────────

    @abstractmethod
    async def sign_bytes(
        self,
        key: KeyRef,
        payload: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        """
        Produce one or more detached signatures over raw bytes.

        Returns:
          Sequence[Signature] (typically length 1). Multiple signatures MAY be
          returned if the provider is configured to co‑sign (e.g., hardware + software).
        """
        ...

    @abstractmethod
    async def sign_digest(
        self,
        key: KeyRef,
        digest: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        """Produce detached signatures over a pre-computed message digest."""
        ...

    @abstractmethod
    async def verify_bytes(
        self,
        payload: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        """
        Verify detached signatures over raw bytes.

        Parameters:
          signatures : sequence of Signature mappings.
          require    : optional policy hints, e.g. {"min_signers": 1, "algs": ["Ed25519"]}

        Returns:
          True if the verification criteria are met, False otherwise.
        """
        ...

    @abstractmethod
    async def verify_digest(
        self,
        digest: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        """Verify detached signatures that were created over a message digest."""
        ...

    # ────────────────────────────────── Envelopes ──────────────────────────────────

    @abstractmethod
    async def canonicalize_envelope(
        self,
        env: Envelope,
        *,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        """
        Deterministically canonicalize an envelope to bytes prior to signing/verifying.

        Implementations MUST document the exact canonicalization performed for each
        'canon' token and ensure stable byte output for semantically identical envelopes.
        """
        ...

    @abstractmethod
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
        Produce one or more detached signatures over a canonicalized envelope.
        """
        ...

    @abstractmethod
    async def sign_stream(
        self,
        key: KeyRef,
        payload: StreamLike,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        """Produce signatures while reading from an iterable or async iterable of bytes."""
        ...

    @abstractmethod
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
        Verify detached signatures against the canonicalized envelope.

        'require' can express policy such as:
          {"min_signers": 2, "algs": ["Ed25519", "RSA-PSS-SHA256"], "kids": ["..."]}
        """
        ...

    @abstractmethod
    async def verify_stream(
        self,
        payload: StreamLike,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        """Verify signatures produced over stream-based signing operations."""
        ...
