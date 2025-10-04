"""Tests covering signing orchestration performed by :class:`EmbedSigner`."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from EmbeddedSigner import EmbedSigner
from swarmauri_core.keys.IKeyProvider import IKeyProvider
from swarmauri_core.signing.types import Signature


@dataclass
class _RecordedCall:
    fmt: str
    key: Any
    payload: bytes
    alg: Any
    opts: Mapping[str, Any] | None


class _FakeEmbedder:
    def __init__(self) -> None:
        self.calls: list[tuple[str, bytes, str, str | None]] = []

    def embed(self, data: bytes, xmp_xml: str, path: str | None) -> bytes:
        self.calls.append(("embed", data, xmp_xml, path))
        return data + xmp_xml.encode("utf-8")

    def read(
        self, data: bytes, path: str | None
    ) -> str | None:  # pragma: no cover - unused in signing tests
        return None

    def remove(
        self, data: bytes, path: str | None
    ) -> bytes:  # pragma: no cover - unused in signing tests
        return data


class _FakeMediaSigner:
    def __init__(self) -> None:
        self.calls: list[_RecordedCall] = []
        self._formats = (
            "JWSSigner",
            "CMSSigner",
            "OpenPGPSigner",
            "PDFSigner",
            "XMLDSigner",
        )

    async def sign_bytes(
        self,
        fmt: str,
        key: Any,
        payload: bytes,
        *,
        alg: str | None = None,
        opts: Mapping[str, Any] | None = None,
    ) -> Sequence[Signature]:
        self.calls.append(_RecordedCall(fmt, key, payload, alg, opts))
        attached = True if opts is None else bool(opts.get("attached", True))
        mode = "attached" if attached else "detached"
        return [
            Signature(
                kid=None,
                version=None,
                format=fmt,
                mode=mode,
                alg=str(alg or "unspecified"),
                artifact=payload,
            )
        ]

    def supported_formats(self) -> Sequence[str]:
        return self._formats


class _StubKeyProvider(IKeyProvider):
    def __init__(self, mapping: Mapping[tuple[str, int], Any]) -> None:
        self._mapping = dict(mapping)
        self.requests: list[tuple[str, tuple[Any, ...]]] = []

    def supports(
        self,
    ) -> Mapping[str, Sequence[str]]:  # pragma: no cover - capability unused
        return {}

    async def create_key(self, spec):  # pragma: no cover - unused in tests
        raise NotImplementedError

    async def import_key(
        self, spec, material: bytes, *, public: bytes | None = None
    ):  # pragma: no cover - unused
        raise NotImplementedError

    async def rotate_key(
        self, kid: str, *, spec_overrides: dict | None = None
    ):  # pragma: no cover - unused
        raise NotImplementedError

    async def destroy_key(
        self, kid: str, version: int | None = None
    ) -> bool:  # pragma: no cover - unused
        return False

    async def get_key(
        self,
        kid: str,
        version: int | None = None,
        *,
        include_secret: bool = False,
    ) -> Any:
        self.requests.append(("get_key", (kid, version, include_secret)))
        key_version = version or 1
        return self._mapping[(kid, key_version)]

    async def get_key_by_ref(
        self,
        key_ref: str,
        *,
        include_secret: bool = False,
    ) -> Any:
        self.requests.append(("get_key_by_ref", (key_ref, include_secret)))
        if key_ref == "ref-token":
            return self._mapping[(key_ref, 1)]
        raise NotImplementedError

    async def list_versions(
        self, kid: str
    ) -> tuple[int, ...]:  # pragma: no cover - unused
        return (1,)

    async def get_public_jwk(
        self, kid: str, version: int | None = None
    ) -> dict:  # pragma: no cover - unused
        raise NotImplementedError

    async def jwks(
        self, *, prefix_kids: str | None = None
    ) -> dict:  # pragma: no cover - unused
        raise NotImplementedError

    async def random_bytes(self, n: int) -> bytes:  # pragma: no cover - unused
        return b"\x00" * n

    async def hkdf(
        self,
        ikm: bytes,
        *,
        salt: bytes,
        info: bytes,
        length: int,
    ) -> bytes:  # pragma: no cover - unused
        return b"\x00" * length


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    "fmt, attached",
    [
        ("JWSSigner", True),
        ("JWSSigner", False),
        ("CMSSigner", True),
        ("CMSSigner", False),
        ("OpenPGPSigner", True),
        ("OpenPGPSigner", False),
        ("PDFSigner", True),
        ("PDFSigner", False),
        ("XMLDSigner", True),
        ("XMLDSigner", False),
    ],
)
async def test_sign_bytes_propagates_attached_flag(fmt: str, attached: bool) -> None:
    embedder = _FakeEmbedder()
    media = _FakeMediaSigner()
    signer = EmbedSigner(embedder=embedder, signer=media)
    payload = b"payload"
    xmp = "<x:xmpmeta><rdf:RDF/></x:xmpmeta>"
    embedded, signatures = await signer.embed_and_sign_bytes(
        payload,
        fmt=fmt,
        xmp_xml=xmp,
        key={"kind": "raw", "key": b"x" * 32},
        attached=attached,
    )
    assert embedded.endswith(xmp.encode("utf-8"))
    assert signatures[0].mode == ("attached" if attached else "detached")
    call = media.calls[-1]
    assert call.fmt == fmt
    assert call.opts is not None
    assert call.opts.get("attached", True) is attached


@pytest.mark.asyncio()
async def test_embed_and_sign_file_writes_back(tmp_path: Path) -> None:
    embedder = _FakeEmbedder()
    media = _FakeMediaSigner()
    signer = EmbedSigner(embedder=embedder, signer=media)
    file_path = tmp_path / "asset.bin"
    file_path.write_bytes(b"abc")

    await signer.embed_and_sign_file(
        file_path,
        fmt="JWSSigner",
        xmp_xml="<x/>",
        key={"kind": "raw", "key": b"y" * 32},
        write_back=True,
    )

    assert file_path.read_bytes().endswith(b"<x/>")
    assert embedder.calls


@pytest.mark.asyncio()
async def test_key_provider_resolution_via_reference() -> None:
    provider = _StubKeyProvider(
        {
            ("abc", 1): {"kid": "abc", "version": 1},
            ("ref-token", 1): {"kid": "from-ref", "version": 1},
        }
    )
    embedder = _FakeEmbedder()
    media = _FakeMediaSigner()
    signer = EmbedSigner(
        embedder=embedder,
        signer=media,
        provider_plugins={"custom": lambda: provider},
    )

    await signer.sign_bytes(
        "JWSSigner",
        key="custom://abc",
        payload=b"data",
        attached=False,
    )
    await signer.sign_bytes(
        "JWSSigner",
        key="custom:ref-token",
        payload=b"data2",
        attached=True,
    )

    assert [req[0] for req in provider.requests] == [
        "get_key_by_ref",
        "get_key",
        "get_key_by_ref",
    ]


@pytest.mark.asyncio()
async def test_sign_file_uses_media_signer(tmp_path: Path) -> None:
    embedder = _FakeEmbedder()
    media = _FakeMediaSigner()
    signer = EmbedSigner(embedder=embedder, signer=media)
    file_path = tmp_path / "payload.bin"
    file_path.write_bytes(b"payload")

    await signer.sign_file(
        file_path,
        fmt="JWSSigner",
        key={"kid": "k", "kind": "raw", "key": b"\x00" * 32},
        attached=False,
        alg="HS256",
    )

    call = media.calls[-1]
    assert call.payload == b"payload"
    assert call.alg == "HS256"
    assert call.opts is not None and call.opts.get("attached") is False
