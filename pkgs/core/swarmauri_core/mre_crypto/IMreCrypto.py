"""
IMreCrypto: Multi‑Recipient Encryption (MRE) provider interface.

Design (agreed)
---------------
- ONE interface with pluggable *modes* (e.g., KEM+AEAD headers, sealed-per-recipient,
  sealed-CEK+AEAD). Providers implement only the subset they support and advertise
  via `supports()`.
- Signing/verification is OUT-OF-SCOPE here (use swarmauri_core.signing.IEnvelopeSign).
- Header-only batch DEK distribution (no payload) is OUT-OF-SCOPE here; if needed,
  use the optional mix‑in `swarmauri_core.mre_crypto.IMreWrap`.

Key concepts
------------
- payload_alg: AEAD used for the content (if the chosen mode uses a shared AEAD).
- recipient_alg: algorithm used for each recipient’s header (wrap/seal).
- mode: a value from MreMode (see swarmauri_core.mre_crypto.types.MreMode).
- envelope: a structured MultiRecipientEnvelope (see .types) holding the payload
  (or per‑recipient sealed payloads) and recipient headers.

Typical non‑sealed flow (KEM+AEAD):
  1) Generate CEK
  2) AEAD‑encrypt plaintext once
  3) Per‑recipient: protect CEK via recipient_alg
  4) Emit one shared ciphertext + N recipient headers

Typical sealed flow:
  - Either seal the payload per‑recipient (no shared AEAD), or seal a CEK per‑recipient
    and use an outer AEAD for the payload (sealed‑CEK+AEAD).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Iterable, Mapping, Optional, Sequence

from ..crypto.types import Alg, KeyRef
from .types import (
    MultiRecipientEnvelope,
    RecipientId,
    MreMode,
)


class IMreCrypto(ABC):
    @abstractmethod
    def supports(self) -> Dict[str, Iterable[str | MreMode]]:
        """
        Return a capability map describing supported algorithms, modes, and features.
        Providers SHOULD list only what they actually implement.

        Keys (omit any you do not support):
          - "payload": iterable[str] of AEAD algorithms usable for the shared payload.
                       (Only relevant for modes that use a shared AEAD.)
          - "recipient": iterable[str] of recipient protection algorithms
                         (e.g., "OpenPGP", "X25519-SEAL", "RSA-OAEP-SHA256", "AES-KW").
          - "modes": iterable[MreMode|str] of supported composition modes.
          - "features": iterable[str] of optional features (e.g., "aad",
                        "threshold", "rewrap_without_reencrypt").

        Example:
            return {
              "payload": ("AES-256-GCM", "XCHACHA20-POLY1305"),
              "recipient": ("OpenPGP", "X25519-SEAL"),
              "modes": (MreMode.ENC_ONCE_HEADERS, MreMode.SEALED_CEK_AEAD),
              "features": ("aad", "rewrap_without_reencrypt"),
            }
        """
        ...

    # ─────────────────── Encrypt (N recipients) ───────────────────

    @abstractmethod
    async def encrypt_for_many(
        self,
        recipients: Sequence[KeyRef],
        pt: bytes,
        *,
        payload_alg: Optional[Alg] = None,
        recipient_alg: Optional[Alg] = None,
        mode: Optional[MreMode | str] = None,
        aad: Optional[bytes] = None,
        shared: Optional[Mapping[str, bytes]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> MultiRecipientEnvelope:
        """
        Encrypt 'pt' for all 'recipients' and return a single MultiRecipientEnvelope.

        Parameters:
          recipients     : public-key KeyRefs (or handles) for each recipient.
          pt             : plaintext bytes.
          payload_alg    : AEAD for the shared payload (if required by the mode).
          recipient_alg  : per‑recipient protection algorithm (wrap/seal).
          mode           : MRE composition mode (see supports()["modes"]).
          aad            : Additional Authenticated Data (supported only by AEAD modes).
          shared         : optional map of app-defined fields to bind/version with envelope.
          opts           : provider hints (e.g., {"threshold_k": 2}).

        Returns:
          MultiRecipientEnvelope with:
            - top-level metadata (mode, payload_alg, recipient_alg, etc.),
            - either a shared AEAD payload or per‑recipient sealed payloads,
            - recipient header list with the material needed to open.
        """
        ...

    # ───────────────── Open (single / many IDs) ─────────────────

    @abstractmethod
    async def open_for(
        self,
        my_identity: KeyRef,
        env: MultiRecipientEnvelope,
        *,
        aad: Optional[bytes] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        """
        Open 'env' using a single private identity.

        Parameters:
          my_identity : private-key KeyRef (or HSM handle) corresponding to one recipient.
          env         : envelope produced by encrypt_for_many.
          aad         : AAD value (must match for AEAD modes).
          opts        : optional hints (e.g., {"prefer_handle": True}).

        Returns:
          plaintext bytes.

        Raises on authentication failure, unsupported mode/alg, or identity mismatch.
        """
        ...

    @abstractmethod
    async def open_for_many(
        self,
        my_identities: Sequence[KeyRef],
        env: MultiRecipientEnvelope,
        *,
        aad: Optional[bytes] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        """
        Attempt to open 'env' with any of the provided identities. Useful when a service
        has multiple keys/slots or when a scheme requires multiple partial openings.

        Parameters:
          my_identities : sequence of private-key KeyRefs / handles.
          env           : envelope to open.
          aad           : AAD (if required by the mode).
          opts          : optional hints (e.g., {"threshold_parts": {...}}).

        Returns:
          plaintext bytes on success.

        Raises on failure to satisfy the scheme (e.g., threshold unmet).
        """
        ...

    # ───────────────── Recipient‑set management ─────────────────

    @abstractmethod
    async def rewrap(
        self,
        env: MultiRecipientEnvelope,
        *,
        add: Optional[Sequence[KeyRef]] = None,
        remove: Optional[Sequence[RecipientId]] = None,
        recipient_alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> MultiRecipientEnvelope:
        """
        Modify the recipient set, re‑wrapping headers without re‑encrypting the payload
        when the mode permits.

        Parameters:
          env            : existing envelope.
          add            : recipients to grant (append headers).
          remove         : recipient IDs to revoke (drop headers).
          recipient_alg  : optionally switch the per‑recipient protection algorithm.
          opts           : hints (e.g., {"rotate_payload_on_revoke": True}).

        Returns:
          Updated MultiRecipientEnvelope.

        Notes:
          - If safe header removal is not possible for the mode (e.g., sealed-per-recipient
            payload), providers SHOULD rotate the payload key and re‑encrypt.
          - Providers SHOULD document complexity: header‑only O(1) vs payload re‑encrypt O(N).
        """
        ...
