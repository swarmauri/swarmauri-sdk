from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from swarmauri_core.crypto.ICrypto import ICrypto
from swarmauri_core.crypto.types import (
    AEADCiphertext,
    Alg,
    KeyRef,
    MultiRecipientEnvelope,
    WrappedKey,
    UnsupportedAlgorithm,
)
from swarmauri_base.ComponentBase import ComponentBase


def _norm_alg(a: Optional[Alg]) -> Optional[Alg]:
    if a is None:
        return None
    # keep it stable but insensitive to simple stylistic variants
    return str(a).strip()


class CompositeCrypto(ICrypto, ComponentBase):
    """Algorithm-routing crypto provider.

    Delegates to the first child that advertises support for the requested algorithm.
    """

    def __init__(self, providers: Sequence[ICrypto]) -> None:
        super().__init__()
        self._providers: Tuple[ICrypto, ...] = tuple(providers)
        if not self._providers:
            raise ValueError("CompositeCrypto requires at least one provider")

    # -------- capability surfacing --------
    def supports(self) -> Dict[str, Iterable[Alg]]:
        agg: Dict[str, List[Alg]] = {}
        for p in self._providers:
            for k, v in p.supports().items():
                agg.setdefault(k, [])
                for a in v:
                    if a not in agg[k]:
                        agg[k].append(a)
        return {k: tuple(v) for k, v in agg.items()}

    # -------- routing helpers --------
    def _pick(self, area: str, alg: Optional[Alg]) -> ICrypto:
        alg_n = _norm_alg(alg)
        # If caller passed None for the algorithm, we let providers apply their own default;
        # pick the first provider advertising *any* alg for that area.
        for p in self._providers:
            caps = p.supports()
            if area not in caps:
                continue
            if alg_n is None:
                # any alg for this area is fine
                if caps[area]:
                    return p
            else:
                if any(_norm_alg(a) == alg_n for a in caps[area]):
                    return p
        raise UnsupportedAlgorithm(f"No provider supports {area} with alg={alg_n!r}")

    # -------- AEAD --------
    async def encrypt(
        self,
        key: KeyRef,
        pt: bytes,
        *,
        alg: Optional[Alg] = None,
        aad: Optional[bytes] = None,
        nonce: Optional[bytes] = None,
    ) -> AEADCiphertext:
        return await self._pick("encrypt", alg).encrypt(
            key, pt, alg=alg, aad=aad, nonce=nonce
        )

    async def decrypt(
        self,
        key: KeyRef,
        ct: AEADCiphertext,
        *,
        aad: Optional[bytes] = None,
    ) -> bytes:
        return await self._pick("decrypt", ct.alg).decrypt(key, ct, aad=aad)

    # -------- wrap / unwrap --------
    async def wrap(
        self,
        kek: KeyRef,
        *,
        dek: Optional[bytes] = None,
        wrap_alg: Optional[Alg] = None,
        nonce: Optional[bytes] = None,
        aad: Optional[bytes] = None,
    ) -> WrappedKey:
        return await self._pick("wrap", wrap_alg).wrap(
            kek, dek=dek, wrap_alg=wrap_alg, nonce=nonce, aad=aad
        )

    async def unwrap(self, kek: KeyRef, wrapped: WrappedKey) -> bytes:
        return await self._pick("unwrap", wrapped.wrap_alg).unwrap(kek, wrapped)

    # -------- for-many --------
    async def encrypt_for_many(
        self,
        recipients: Iterable[KeyRef],
        pt: bytes,
        *,
        enc_alg: Optional[Alg] = None,
        recipient_wrap_alg: Optional[Alg] = None,
        aad: Optional[bytes] = None,
        nonce: Optional[bytes] = None,
    ) -> MultiRecipientEnvelope:
        # Route primarily by enc_alg; if None, pick a provider that supports "encrypt" and has for_many.
        return await self._pick("encrypt", enc_alg).encrypt_for_many(
            recipients,
            pt,
            enc_alg=enc_alg,
            recipient_wrap_alg=recipient_wrap_alg,
            aad=aad,
            nonce=nonce,
        )

    # -------- seal / unseal (explicit) --------
    async def seal(
        self, recipient: KeyRef, pt: bytes, *, alg: Optional[Alg] = None
    ) -> bytes:
        return await self._pick("seal", alg).seal(recipient, pt, alg=alg)

    async def unseal(
        self,
        recipient_priv: KeyRef,
        sealed: bytes,
        *,
        alg: Optional[Alg] = None,
    ) -> bytes:
        # Some providers embed alg tag in sealed blob; we still require alg for routing clarity.
        return await self._pick("unseal", alg).unseal(recipient_priv, sealed, alg=alg)
