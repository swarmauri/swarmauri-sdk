from __future__ import annotations

import hashlib
import secrets
from typing import (
    Any,
    Dict,
    Iterable,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Protocol,
    runtime_checkable,
    Literal,
)

from swarmauri_core.mre_crypto.types import MultiRecipientEnvelope, RecipientId, MreMode
from swarmauri_core.crypto.types import Alg, KeyRef
from swarmauri_base.mre_crypto import MreCryptoBase

try:  # pragma: no cover - handled in runtime
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM, XChaCha20Poly1305

    _CRYPTO_OK = True
    _XCHACHA_OK = True
except Exception:  # pragma: no cover
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM  # type: ignore

        _CRYPTO_OK = True
        _XCHACHA_OK = False
    except Exception:
        _CRYPTO_OK = False
        _XCHACHA_OK = False


VALID_AEAD_ALGS = (
    ("AES-256-GCM", "XCHACHA20-POLY1305") if _XCHACHA_OK else ("AES-256-GCM",)
)


@runtime_checkable
class KeyringClient(Protocol):
    """Minimal protocol an external KMS/HSM 'keyring' client must implement."""

    def id(self) -> str:
        """Stable identifier for this keyring."""

    async def wrap_cek(self, cek: bytes, *, context: Mapping[str, bytes]) -> bytes:
        """Return an opaque header which lets this keyring later release the same CEK."""

    async def unwrap_cek(self, header: bytes, *, context: Mapping[str, bytes]) -> bytes:
        """Return the CEK if the caller is authorized and policy is satisfied."""


class _AEAD:
    @staticmethod
    def encrypt_with_key(
        cek: bytes, pt: bytes, *, alg: str, aad: Optional[bytes]
    ) -> Tuple[bytes, bytes]:
        if not _CRYPTO_OK:
            raise RuntimeError(
                "KeyringMreCrypto requires 'cryptography' package. Install with: pip install cryptography"
            )
        if alg == "AES-256-GCM":
            if len(cek) not in (16, 24, 32):
                raise ValueError(
                    "AES-GCM expects 128/192/256-bit key (16/24/32 bytes)."
                )
            nonce = secrets.token_bytes(12)
            ct = AESGCM(cek).encrypt(nonce, pt, aad)
            return nonce, ct
        if alg == "XCHACHA20-POLY1305":
            if not _XCHACHA_OK:
                raise ValueError(
                    "XChaCha20-Poly1305 not supported in this environment."
                )
            if len(cek) != 32:
                raise ValueError("XChaCha20-Poly1305 expects 256-bit key (32 bytes).")
            nonce = secrets.token_bytes(24)
            ct = XChaCha20Poly1305(cek).encrypt(nonce, pt, aad)
            return nonce, ct
        raise ValueError(f"Unsupported payload AEAD alg: {alg}")

    @staticmethod
    def decrypt_with_key(
        cek: bytes, nonce: bytes, ct: bytes, *, alg: str, aad: Optional[bytes]
    ) -> bytes:
        if not _CRYPTO_OK:
            raise RuntimeError(
                "KeyringMreCrypto requires 'cryptography' package. Install with: pip install cryptography"
            )

        if alg == "AES-256-GCM":
            return AESGCM(cek).decrypt(nonce, ct, aad)

        if alg == "XCHACHA20-POLY1305":
            if not _XCHACHA_OK:
                raise ValueError(
                    "XChaCha20-Poly1305 not supported in this environment."
                )
            return XChaCha20Poly1305(cek).decrypt(nonce, ct, aad)

        raise ValueError(f"Unsupported payload AEAD alg: {alg}")


class KeyringMreCrypto(MreCryptoBase):
    """MRE provider using multiple independent keyrings/HSMs."""

    type: Literal["KeyringMreCrypto"] = "KeyringMreCrypto"

    def __init__(self, **data: Any) -> None:
        if not _CRYPTO_OK:
            raise RuntimeError(
                "KeyringMreCrypto requires 'cryptography' package. Install with: pip install cryptography"
            )
        super().__init__(**data)

    def supports(self) -> Dict[str, Iterable[str | MreMode]]:
        return {
            "payload": VALID_AEAD_ALGS,
            "recipient": ("KEYRING",),
            "modes": (MreMode.SEALED_CEK_AEAD,),
            "features": ("aad", "rewrap_without_reencrypt"),
        }

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
        if not recipients:
            raise ValueError("encrypt_for_many: 'recipients' must be non-empty.")

        mode = MreMode(mode or MreMode.SEALED_CEK_AEAD)
        if mode is not MreMode.SEALED_CEK_AEAD:
            raise ValueError(f"Unsupported mode for KeyringMreCrypto: {mode}")

        recipient_alg = recipient_alg or "KEYRING"
        if recipient_alg != "KEYRING":
            raise ValueError("KeyringMreCrypto only supports recipient_alg='KEYRING'.")

        payload_alg = payload_alg or "AES-256-GCM"
        if payload_alg not in VALID_AEAD_ALGS:
            raise ValueError(f"Unsupported payload AEAD alg: {payload_alg}")

        quorum_k = int((opts or {}).get("quorum_k", len(recipients)))
        if not (1 <= quorum_k <= len(recipients)):
            raise ValueError("opts['quorum_k'] must satisfy 1 <= k <= len(recipients).")

        cek_len = 32
        cek = secrets.token_bytes(cek_len)
        nonce, ct = _AEAD.encrypt_with_key(cek, pt, alg=payload_alg, aad=aad)

        recipient_entries: list[dict[str, Any]] = []
        for keyref in recipients:
            client, r_context = self._extract_keyring_client(keyref)
            header = await client.wrap_cek(
                cek, context=self._default_context(shared).update_copy(r_context)
            )
            rid = self._stable_id(client)
            recipient_entries.append({"id": rid, "header": header})

        return {
            "mode": str(MreMode.SEALED_CEK_AEAD),
            "recipient_alg": "KEYRING",
            "payload": {
                "kind": "aead",
                "alg": payload_alg,
                "nonce": nonce,
                "ct": ct,
                "aad": aad,
            },
            "recipients": recipient_entries,
            "shared": dict(shared or {}),
            "meta": {"quorum_k": quorum_k, "recipients_m": len(recipient_entries)},
        }

    async def open_for_many(
        self,
        my_identities: Sequence[KeyRef],
        env: MultiRecipientEnvelope,
        *,
        aad: Optional[bytes] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        if not my_identities:
            raise ValueError("open_for_many: 'my_identities' must be non-empty.")

        self._assert_env_shape(env)
        meta = env.get("meta", {}) or {}
        quorum_k = int(meta.get("quorum_k", 1))
        recips = env["recipients"]
        if quorum_k < 1:
            raise ValueError("Envelope meta.quorum_k must be >= 1.")

        headers_by_id: Dict[str, bytes] = {r["id"]: r["header"] for r in recips}
        shared: Mapping[str, bytes] = env.get("shared") or {}
        recovered: Dict[bytes, int] = {}
        payload = env["payload"]
        payload_alg = payload["alg"]
        payload_nonce = payload["nonce"]
        payload_ct = payload["ct"]
        aad_env = payload.get("aad", None)
        aad_to_check = aad if aad is not None else aad_env
        if aad_to_check != aad_env:
            raise ValueError("AAD mismatch for AEAD mode.")

        for keyref in my_identities:
            client, id_context = self._extract_keyring_client(keyref)
            rid = self._stable_id(client)
            try_ids: Sequence[str] = (
                [rid] if rid in headers_by_id else list(headers_by_id.keys())
            )

            for hdr_id in try_ids:
                header = headers_by_id[hdr_id]
                try:
                    cek = await client.unwrap_cek(
                        header,
                        context=self._default_context(shared).update_copy(id_context),
                    )
                    recovered[cek] = recovered.get(cek, 0) + 1
                    if recovered[cek] >= quorum_k:
                        return _AEAD.decrypt_with_key(
                            cek,
                            payload_nonce,
                            payload_ct,
                            alg=payload_alg,
                            aad=aad_to_check,
                        )
                except Exception:
                    continue

        raise PermissionError(f"Unable to satisfy CEK quorum (required {quorum_k}).")

    async def open_for(
        self,
        my_identity: KeyRef,
        env: MultiRecipientEnvelope,
        *,
        aad: Optional[bytes] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        return await self.open_for_many([my_identity], env, aad=aad, opts=opts)

    async def rewrap(
        self,
        env: MultiRecipientEnvelope,
        *,
        add: Optional[Sequence[KeyRef]] = None,
        remove: Optional[Sequence[RecipientId]] = None,
        recipient_alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> MultiRecipientEnvelope:
        self._assert_env_shape(env)
        if recipient_alg not in (None, "KEYRING"):
            raise ValueError("KeyringMreCrypto only supports recipient_alg='KEYRING'.")

        add = add or []
        remove = remove or []
        shared: Mapping[str, bytes] = env.get("shared") or {}

        rotate_on_revoke = bool((opts or {}).get("rotate_payload_on_revoke", False))

        if remove or rotate_on_revoke:
            identities = (opts or {}).get("identities", None)
            if not isinstance(identities, (list, tuple)) or not identities:
                raise ValueError(
                    "rewrap with removal/rotation requires opts['identities']: Sequence[KeyRef] able to meet quorum."
                )
            cek = await self._recover_cek_for_env(env, identities, shared)
        else:
            cek = await self._recover_cek_if_present(env, shared, opts)

        if remove:
            kept = [r for r in env["recipients"] if r["id"] not in set(remove)]
        else:
            kept = list(env["recipients"])

        if rotate_on_revoke:
            payload = env["payload"]
            payload_alg = payload["alg"]
            pt = _AEAD.decrypt_with_key(
                cek,
                payload["nonce"],
                payload["ct"],
                alg=payload_alg,
                aad=payload.get("aad"),
            )
            new_cek = secrets.token_bytes(len(cek))
            new_nonce, new_ct = _AEAD.encrypt_with_key(
                new_cek, pt, alg=payload_alg, aad=payload.get("aad")
            )
            env["payload"]["nonce"] = new_nonce
            env["payload"]["ct"] = new_ct
            cek = new_cek
            meta = dict(env.get("meta") or {})
            meta["rotated_at"] = meta.get("rotated_at", 0) + 1
            env["meta"] = meta

        for keyref in add:
            client, a_context = self._extract_keyring_client(keyref)
            header = await client.wrap_cek(
                cek, context=self._default_context(shared).update_copy(a_context)
            )
            rid = self._stable_id(client)
            kept.append({"id": rid, "header": header})

        env["recipients"] = kept
        return env

    async def _recover_cek_if_present(
        self,
        env: MultiRecipientEnvelope,
        shared: Mapping[str, bytes],
        opts: Optional[Mapping[str, object]],
    ) -> bytes:
        identities = (opts or {}).get("identities")
        if not identities:
            raise RuntimeError(
                "CEK recovery requested but no opts['identities'] provided."
            )
        return await self._recover_cek_for_env(env, identities, shared)

    async def _recover_cek_for_env(
        self,
        env: MultiRecipientEnvelope,
        identities: Sequence[KeyRef],
        shared: Mapping[str, bytes],
    ) -> bytes:
        meta = env.get("meta", {}) or {}
        quorum_k = int(meta.get("quorum_k", 1))
        recipients = env["recipients"]
        headers_by_id: Dict[str, bytes] = {r["id"]: r["header"] for r in recipients}
        recovered: Dict[bytes, int] = {}

        for keyref in identities:
            client, id_context = self._extract_keyring_client(keyref)
            rid = self._stable_id(client)
            try_ids: Sequence[str] = (
                [rid] if rid in headers_by_id else list(headers_by_id.keys())
            )
            for hdr_id in try_ids:
                header = headers_by_id[hdr_id]
                try:
                    cek = await client.unwrap_cek(
                        header,
                        context=self._default_context(shared).update_copy(id_context),
                    )
                    recovered[cek] = recovered.get(cek, 0) + 1
                    if recovered[cek] >= quorum_k:
                        return cek
                except Exception:
                    continue

        raise PermissionError(
            f"Unable to satisfy CEK quorum (required {quorum_k}) for CEK recovery."
        )

    def _assert_env_shape(self, env: Mapping[str, Any]) -> None:
        if env.get("mode") != str(MreMode.SEALED_CEK_AEAD):
            raise ValueError(
                "Envelope mode must be 'sealed_cek+aead' for KeyringMreCrypto."
            )
        payload = env.get("payload")
        if not isinstance(payload, Mapping) or payload.get("kind") != "aead":
            raise ValueError("Envelope payload must be an AEAD payload.")
        if payload.get("alg") not in VALID_AEAD_ALGS:
            raise ValueError("Unsupported payload AEAD in envelope.")
        if not isinstance(env.get("recipients"), list):
            raise ValueError("Envelope missing 'recipients' list.")

    def _extract_keyring_client(
        self, keyref: KeyRef
    ) -> Tuple[KeyringClient, Dict[str, bytes]]:
        if isinstance(keyref, dict) and keyref.get("kind") == "keyring_client":
            client = keyref.get("client")
            context = keyref.get("context") or {}
            if not isinstance(context, dict) or not all(
                isinstance(k, str) and isinstance(v, (bytes, bytearray))
                for k, v in context.items()
            ):
                raise TypeError("KeyRef['context'] must be a dict[str, bytes].")
            if isinstance(client, KeyringClient) or (
                isinstance(client, object)
                and hasattr(client, "wrap_cek")
                and hasattr(client, "unwrap_cek")
                and hasattr(client, "id")
            ):
                return client, dict(context)
        raise TypeError(
            "KeyRef must be {'kind':'keyring_client','client':KeyringClient,'context'?:{str:bytes}}."
        )

    def _stable_id(self, client: KeyringClient) -> str:
        raw = client.id().encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    class _Ctx(dict):
        def update_copy(self, extras: Mapping[str, bytes]) -> "KeyringMreCrypto._Ctx":
            d = KeyringMreCrypto._Ctx(self)
            d.update(extras)
            return d

    def _default_context(self, shared: Mapping[str, bytes]) -> "KeyringMreCrypto._Ctx":
        return KeyringMreCrypto._Ctx(shared or {})
