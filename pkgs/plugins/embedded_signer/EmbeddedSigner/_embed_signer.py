"""Embed XMP metadata and sign media payloads with Swarmauri plugins."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path
from typing import Any, MutableMapping, Optional
from urllib.parse import parse_qs, urlparse

from EmbedXMP import EmbedXMP
from MediaSigner import MediaSigner
from swarmauri_core.crypto.types import KeyRef
from swarmauri_core.keys.IKeyProvider import IKeyProvider
from swarmauri_core.signing.types import Signature


@dataclass(frozen=True)
class _ParsedKeyRef:
    provider: Optional[str]
    kid: str
    version: Optional[int]


class EmbedSigner:
    """High-level helper that embeds XMP metadata and produces signatures."""

    def __init__(
        self,
        *,
        embedder: Optional[EmbedXMP] = None,
        signer: Optional[MediaSigner] = None,
        key_provider: Optional[IKeyProvider] = None,
        key_provider_name: Optional[str] = None,
        provider_plugins: Optional[
            Mapping[str, Callable[[], IKeyProvider] | type[IKeyProvider]]
        ] = None,
        eager_import: bool = True,
    ) -> None:
        self._embedder = embedder or EmbedXMP(eager_import=eager_import)
        self._provider_factories: MutableMapping[
            str, Callable[[], IKeyProvider] | type[IKeyProvider]
        ] = self._discover_provider_factories()
        if provider_plugins:
            self._provider_factories.update(dict(provider_plugins))
        self._providers: MutableMapping[str, IKeyProvider] = {}
        self._default_provider: Optional[IKeyProvider] = None
        self._default_provider_name: Optional[str] = None

        if key_provider is not None:
            self._default_provider = key_provider
            self._default_provider_name = key_provider.__class__.__name__
        elif key_provider_name is not None:
            self._default_provider = self._instantiate_provider(key_provider_name)
            self._default_provider_name = key_provider_name

        provider_for_signer = self._default_provider
        self._signer = signer or MediaSigner(key_provider=provider_for_signer)

    # ------------------------------------------------------------------
    @staticmethod
    def _discover_provider_factories() -> MutableMapping[
        str, Callable[[], IKeyProvider] | type[IKeyProvider]
    ]:
        factories: MutableMapping[
            str, Callable[[], IKeyProvider] | type[IKeyProvider]
        ] = {}
        try:
            entries = metadata.entry_points(group="swarmauri.key_providers")
        except TypeError:  # pragma: no cover - Python <3.10 fallback
            entries = metadata.entry_points()["swarmauri.key_providers"]
        for entry in entries:
            try:
                provider_cls = entry.load()
            except (
                Exception
            ):  # pragma: no cover - defensive against broken entry points
                continue
            if not inspect.isclass(provider_cls) and not callable(provider_cls):
                continue
            factories[entry.name] = provider_cls
        return factories

    def _instantiate_provider(self, name: str) -> IKeyProvider:
        if name in self._providers:
            return self._providers[name]
        factory = self._provider_factories.get(name)
        if factory is None:
            raise ValueError(f"Unknown key provider '{name}'")
        provider: IKeyProvider
        if inspect.isclass(factory):
            provider = factory()  # type: ignore[call-arg]
        else:
            provider = factory()
        self._providers[name] = provider
        return provider

    def _get_provider(self, name: Optional[str]) -> IKeyProvider:
        if name is None:
            if self._default_provider is not None:
                return self._default_provider
            if self._default_provider_name is not None:
                return self._instantiate_provider(self._default_provider_name)
            raise ValueError(
                "No default key provider configured; include a provider name in the key reference."
            )
        if name == self._default_provider_name and self._default_provider is not None:
            return self._default_provider
        return self._instantiate_provider(name)

    # ------------------------------------------------------------------
    @staticmethod
    def _parse_key_reference(value: str) -> _ParsedKeyRef:
        parsed = urlparse(value)
        if parsed.scheme:
            provider = parsed.scheme
            kid = (parsed.netloc + parsed.path).lstrip("/")
            query = parse_qs(parsed.query, keep_blank_values=False)
            version = None
            if "version" in query and query["version"]:
                try:
                    version = int(query["version"][0])
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        f"Invalid version component in key reference '{value}'"
                    ) from exc
            return _ParsedKeyRef(provider=provider, kid=kid, version=version)
        token = value
        provider_name = None
        if ":" in token and not token.startswith("{"):
            provider_name, _, token = token.partition(":")
        kid, sep, version_token = token.partition("@")
        version_number = None
        if sep:
            try:
                version_number = int(version_token)
            except ValueError as exc:
                raise ValueError(
                    f"Invalid version component in key reference '{value}'"
                ) from exc
        if not kid:
            raise ValueError("Key reference must include a key identifier")
        return _ParsedKeyRef(provider=provider_name, kid=kid, version=version_number)

    async def _resolve_key(
        self, key: KeyRef | Mapping[str, Any] | str
    ) -> KeyRef | Mapping[str, Any]:
        if isinstance(key, Mapping):
            return key
        if isinstance(key, KeyRef):
            return key
        if isinstance(key, str):
            ref = self._parse_key_reference(key)
            provider = self._get_provider(ref.provider)
            try:
                resolved = await provider.get_key_by_ref(ref.kid, include_secret=True)
            except NotImplementedError:
                resolved = None
            except AttributeError:  # pragma: no cover - provider without method
                resolved = None
            if resolved is None:
                resolved = await provider.get_key(
                    ref.kid, version=ref.version, include_secret=True
                )
            return resolved
        raise TypeError(
            "key must be a Mapping, KeyRef, or string reference understood by EmbedSigner"
        )

    # ------------------------------------------------------------------
    def embed_bytes(
        self, data: bytes, xmp_xml: str, *, path: str | Path | None = None
    ) -> bytes:
        """Embed XMP metadata into *data* using the configured handlers."""

        ref = str(path) if path is not None else None
        return self._embedder.embed(data, xmp_xml, ref)

    def read_xmp(self, data: bytes, *, path: str | Path | None = None) -> str | None:
        """Read XMP metadata from *data* using the configured handlers."""

        ref = str(path) if path is not None else None
        return self._embedder.read(data, ref)

    def remove_xmp(self, data: bytes, *, path: str | Path | None = None) -> bytes:
        """Remove XMP metadata from *data* using the configured handlers."""

        ref = str(path) if path is not None else None
        return self._embedder.remove(data, ref)

    def embed_file(
        self,
        path: str | Path,
        xmp_xml: str,
        *,
        write_back: bool = True,
        output: str | Path | None = None,
    ) -> bytes:
        """Embed XMP metadata directly into a file on disk."""

        file_path = Path(path)
        updated = self.embed_bytes(file_path.read_bytes(), xmp_xml, path=file_path)
        target = Path(output) if output is not None else file_path
        if write_back:
            target.write_bytes(updated)
        return updated

    def read_xmp_file(self, path: str | Path) -> str | None:
        """Read XMP metadata from the file located at *path*."""

        file_path = Path(path)
        return self.read_xmp(file_path.read_bytes(), path=file_path)

    def remove_xmp_file(
        self,
        path: str | Path,
        *,
        write_back: bool = False,
        output: str | Path | None = None,
    ) -> bytes:
        """Remove XMP metadata from a file, optionally persisting the result."""

        file_path = Path(path)
        updated = self.remove_xmp(file_path.read_bytes(), path=file_path)
        target = Path(output) if output is not None else file_path
        if write_back:
            target.write_bytes(updated)
        return updated

    # ------------------------------------------------------------------
    async def sign_bytes(
        self,
        fmt: str,
        key: KeyRef | Mapping[str, Any] | str,
        payload: bytes,
        *,
        attached: bool = True,
        alg: Optional[str] = None,
        signer_opts: Optional[Mapping[str, Any]] = None,
    ) -> Sequence[Signature]:
        """Produce signatures for *payload* using the requested signer format."""

        resolved_key = await self._resolve_key(key)
        opts: dict[str, Any] = dict(signer_opts or {})
        opts.setdefault("attached", attached)
        return await self._signer.sign_bytes(
            fmt, resolved_key, payload, alg=alg, opts=opts
        )

    async def embed_and_sign_bytes(
        self,
        data: bytes,
        *,
        fmt: str,
        xmp_xml: str,
        key: KeyRef | Mapping[str, Any] | str,
        path: str | Path | None = None,
        attached: bool = True,
        alg: Optional[str] = None,
        signer_opts: Optional[Mapping[str, Any]] = None,
    ) -> tuple[bytes, Sequence[Signature]]:
        """Embed metadata into *data* and sign the updated payload."""

        embedded = self.embed_bytes(data, xmp_xml, path=path)
        signatures = await self.sign_bytes(
            fmt,
            key,
            embedded,
            attached=attached,
            alg=alg,
            signer_opts=signer_opts,
        )
        return embedded, signatures

    async def embed_and_sign_file(
        self,
        path: str | Path,
        *,
        fmt: str,
        xmp_xml: str,
        key: KeyRef | Mapping[str, Any] | str,
        attached: bool = True,
        alg: Optional[str] = None,
        signer_opts: Optional[Mapping[str, Any]] = None,
        write_back: bool = False,
    ) -> tuple[bytes, Sequence[Signature]]:
        """Embed metadata into *path* and optionally persist the signed bytes."""

        file_path = Path(path)
        embedded, signatures = await self.embed_and_sign_bytes(
            file_path.read_bytes(),
            fmt=fmt,
            xmp_xml=xmp_xml,
            key=key,
            path=file_path,
            attached=attached,
            alg=alg,
            signer_opts=signer_opts,
        )
        if write_back:
            file_path.write_bytes(embedded)
        return embedded, signatures

    async def sign_file(
        self,
        path: str | Path,
        *,
        fmt: str,
        key: KeyRef | Mapping[str, Any] | str,
        attached: bool = True,
        alg: Optional[str] = None,
        signer_opts: Optional[Mapping[str, Any]] = None,
    ) -> Sequence[Signature]:
        """Sign the contents of *path* and return the generated signatures."""

        file_path = Path(path)
        payload = file_path.read_bytes()
        return await self.sign_bytes(
            fmt,
            key,
            payload,
            attached=attached,
            alg=alg,
            signer_opts=signer_opts,
        )

    # ------------------------------------------------------------------
    def supported_embed_handlers(self) -> Sequence[str]:
        """Return the names of registered XMP handlers."""

        return tuple(
            handler.__class__.__name__
            for handler in getattr(self._embedder, "_handlers", [])
        )

    def supported_signers(self) -> Sequence[str]:
        """Expose signer formats advertised by the underlying :class:`MediaSigner`."""

        return tuple(self._signer.supported_formats())
