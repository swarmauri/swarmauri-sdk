"""
ISigning: Detached signing / verification interface (envelope‑agnostic).

Design goals
------------
- One interface that cleanly supports:
  • Signing/verification of raw bytes.
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
Digest = bytes
ByteStream = Union[Iterable[bytes], AsyncIterable[bytes]]


class ISigning(ABC):
    @abstractmethod
    def supports(self, key_ref: Optional[str] = None) -> Mapping[str, Iterable[str]]:
        """
        Return capability information.

        Keys (omit if unsupported):
          - "algs": iterable of signature algorithms (e.g., "Ed25519", "RSA-PSS-SHA256", "OpenPGP").
          - "canons": iterable of canonicalization identifiers (e.g., "json", "cbor", "json-c14n").
          - "signs": iterable of supported signing operations (e.g., "bytes", "digest", "stream", "envelope").
          - "verifies": iterable of supported verification operations (e.g., "bytes", "digest", "stream", "envelope").
          - "envelopes": iterable describing supported envelope encodings or profiles (e.g., "cms-detached").
          - "features": optional iterable of flags, e.g.:
                • "multi"          → optimized for multi‑signature sets
                • "detached_only"  → only detached signatures (default)
                • "attest"         → can include attestation chains in Signature["chain"]

        When ``key_ref`` is provided the result MAY be specialized for that key.
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

    # ───────────────────────────────── Digest ─────────────────────────────────

    @abstractmethod
    async def sign_digest(
        self,
        key: KeyRef,
        digest: Digest,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        """
        Sign a pre-computed message digest.

        Implementations SHOULD document the digest algorithms supported and how
        they map to signature algorithms.
        """
        ...

    @abstractmethod
    async def verify_digest(
        self,
        digest: Digest,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        """
        Verify detached signatures against a pre-computed message digest.
        """
        ...

    # ───────────────────────────────── Streams ────────────────────────────────

    @abstractmethod
    async def sign_stream(
        self,
        key: KeyRef,
        stream: ByteStream,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        """
        Incrementally sign a byte stream without loading it entirely into memory.

        ``stream`` MAY be synchronous or asynchronous and yields chunks of
        ``bytes``.
        """
        ...

    @abstractmethod
    async def verify_stream(
        self,
        stream: ByteStream,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        """
        Verify detached signatures while streaming the payload.
        """
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
