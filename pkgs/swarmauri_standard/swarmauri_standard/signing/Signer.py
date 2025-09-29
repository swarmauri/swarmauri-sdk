"""Facade that discovers and dispatches to registered signing plugins."""

from __future__ import annotations

from typing import (
    AsyncIterable,
    Iterable,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Union,
)

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.signing.SigningBase import SigningBase
from swarmauri_core.crypto.types import Alg, KeyRef
from swarmauri_core.keys.IKeyProvider import IKeyProvider
from swarmauri_core.signing.types import Signature

try:  # Pragmatic optional imports so plugins self-register when available.
    import swarmauri_signing_cms  # noqa: F401
except Exception:  # pragma: no cover - plugin optional
    pass

try:
    import swarmauri_signing_jws  # noqa: F401
except Exception:  # pragma: no cover - plugin optional
    pass

try:
    import swarmauri_signing_openpgp  # noqa: F401
except Exception:  # pragma: no cover - plugin optional
    pass

try:
    import swarmauri_signing_pades  # noqa: F401
except Exception:  # pragma: no cover - plugin optional
    pass


class Signer(ComponentBase):
    """High-level async facade that routes signing calls to registered plugins."""

    resource: Optional[str] = ResourceTypes.SIGNING.value
    type: str = "Signer"

    def __init__(self, key_provider: Optional[IKeyProvider] = None) -> None:
        super().__init__()
        self._key_provider = key_provider
        self._plugins: MutableMapping[str, SigningBase] = {}
        self._load_plugins()

    # ------------------------------------------------------------------
    def _load_plugins(self) -> None:
        registry_entry = self.__class__._registry.get("SigningBase", {})
        subtypes = registry_entry.get("subtypes", {})
        for type_name, cls in subtypes.items():
            if type_name in self._plugins:
                continue
            plugin = self._instantiate(cls)
            if plugin is not None:
                self._plugins[type_name] = plugin

    def _instantiate(self, cls: type[SigningBase]) -> Optional[SigningBase]:
        try:
            plugin = cls(key_provider=self._key_provider)
        except TypeError:
            plugin = cls()  # type: ignore[call-arg]
        if self._key_provider and hasattr(plugin, "set_key_provider"):
            plugin.set_key_provider(self._key_provider)
        return plugin

    def _resolve(self, fmt: str) -> SigningBase:
        try:
            return self._plugins[fmt]
        except KeyError as exc:  # pragma: no cover - error path
            raise ValueError(
                f"No signing plugin registered for format '{fmt}'"
            ) from exc

    # ------------------------------------------------------------------
    async def sign_bytes(
        self,
        fmt: str,
        key: KeyRef,
        payload: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        return await self._resolve(fmt).sign_bytes(key, payload, alg=alg, opts=opts)

    async def sign_digest(
        self,
        fmt: str,
        key: KeyRef,
        digest: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        return await self._resolve(fmt).sign_digest(key, digest, alg=alg, opts=opts)

    async def verify_bytes(
        self,
        fmt: str,
        payload: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        return await self._resolve(fmt).verify_bytes(
            payload, signatures, require=require, opts=opts
        )

    async def verify_digest(
        self,
        fmt: str,
        digest: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        return await self._resolve(fmt).verify_digest(
            digest, signatures, require=require, opts=opts
        )

    async def canonicalize_envelope(
        self,
        fmt: str,
        env,
        *,
        canon: Optional[str] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        return await self._resolve(fmt).canonicalize_envelope(
            env, canon=canon, opts=opts
        )

    async def sign_envelope(
        self,
        fmt: str,
        key: KeyRef,
        env,
        *,
        alg: Optional[Alg] = None,
        canon: Optional[str] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        return await self._resolve(fmt).sign_envelope(
            key, env, alg=alg, canon=canon, opts=opts
        )

    async def sign_stream(
        self,
        fmt: str,
        key: KeyRef,
        chunks: Union[Iterable[bytes], AsyncIterable[bytes]],
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        return await self._resolve(fmt).sign_stream(key, chunks, alg=alg, opts=opts)

    async def verify_envelope(
        self,
        fmt: str,
        env,
        signatures: Sequence[Signature],
        *,
        canon: Optional[str] = None,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        return await self._resolve(fmt).verify_envelope(
            env, signatures, canon=canon, require=require, opts=opts
        )

    async def verify_stream(
        self,
        fmt: str,
        chunks: Union[Iterable[bytes], AsyncIterable[bytes]],
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        return await self._resolve(fmt).verify_stream(
            chunks, signatures, require=require, opts=opts
        )

    # ------------------------------------------------------------------
    def supported_formats(self) -> Iterable[str]:
        return tuple(self._plugins.keys())

    def supports(
        self, fmt: str, *, key_ref: Optional[str] = None
    ) -> Mapping[str, Iterable[str]]:
        plugin = self._resolve(fmt)
        if key_ref is not None:
            try:
                return plugin.supports(key_ref)  # type: ignore[arg-type]
            except TypeError:
                pass
        return plugin.supports()
