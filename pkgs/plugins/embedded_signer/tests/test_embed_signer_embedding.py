"""Integration tests for XMP embedding via :class:`EmbeddedSigner`."""

from __future__ import annotations

import pytest

from EmbedXMP import EmbedXMP
from EmbeddedSigner import EmbedSigner
from swarmauri_xmp_gif import GIFXMP
from swarmauri_xmp_jpeg import JPEGXMP
from swarmauri_xmp_mp4 import MP4XMP
from swarmauri_xmp_pdf import PDFXMP
from swarmauri_xmp_png import PNGXMP
from swarmauri_xmp_svg import SVGXMP
from swarmauri_xmp_tiff import TIFFXMP
from swarmauri_xmp_webp import WebPXMP


@pytest.fixture()
def embed_signer_all() -> EmbedSigner:
    embedder = EmbedXMP(
        handlers=[GIFXMP, JPEGXMP, PNGXMP, SVGXMP, WebPXMP],
        eager_import=False,
    )
    return EmbedSigner(embedder=embedder)


def _minimal_png() -> bytes:
    import binascii
    import zlib

    def chunk(ctype: bytes, payload: bytes) -> bytes:
        length = len(payload).to_bytes(4, "big")
        crc = (binascii.crc32(ctype + payload) & 0xFFFFFFFF).to_bytes(4, "big")
        return length + ctype + payload + crc

    ihdr = (
        b"\x00\x00\x00\x01"
        + b"\x00\x00\x00\x01"
        + b"\x08"
        + b"\x02"
        + b"\x00"
        + b"\x00"
        + b"\x00"
    )
    idat = zlib.compress(b"\x00\x00\x00\x00")
    return (
        PNGXMP.PNG_SIG
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", idat)
        + chunk(b"IEND", b"")
    )


def _minimal_gif() -> bytes:
    return b"GIF89a" + b"\x01\x00\x01\x00" + b"\x00" + b"\x00" + b"\x00" + b"\x3b"


def _minimal_jpeg() -> bytes:
    return (
        b"\xff\xd8"
        + b"\xff\xe0\x00\x10JFIF\x00\x01\x02\x00\x00\x01\x00\x01\x00\x00"
        + b"\xff\xd9"
    )


def _minimal_svg() -> bytes:
    return (
        "<svg xmlns='http://www.w3.org/2000/svg' xmlns:x='adobe:ns:meta/'>"
        "<rect width='1' height='1'/></svg>"
    ).encode("utf-8")


def _minimal_webp() -> bytes:
    chunk_type = b"VP8 "
    payload = b""
    chunk = chunk_type + len(payload).to_bytes(4, "little") + payload
    body = chunk
    size = len(body) + 4
    return b"RIFF" + size.to_bytes(4, "little") + b"WEBP" + body


@pytest.mark.parametrize(
    "name, payload_factory",
    [
        ("PNGXMP", _minimal_png),
        ("GIFXMP", _minimal_gif),
        ("JPEGXMP", _minimal_jpeg),
        ("SVGXMP", _minimal_svg),
        ("WebPXMP", _minimal_webp),
    ],
)
def test_embed_and_read_round_trip(
    embed_signer_all: EmbedSigner,
    name: str,
    payload_factory,
) -> None:
    payload = payload_factory()
    xmp = "<x:xmpmeta><rdf:RDF/></x:xmpmeta>"

    updated = embed_signer_all.embed_bytes(payload, xmp)
    assert xmp == embed_signer_all.read_xmp(updated)
    stripped = embed_signer_all.remove_xmp(updated)
    assert embed_signer_all.read_xmp(stripped) is None


@pytest.mark.parametrize(
    "handler_cls, payload",
    [
        (MP4XMP, b"\x00\x00\x00\x18ftypmp42"),
        (PDFXMP, b"%PDF-1.4\n%\xe2\xe3\xcf\xd3"),
        (TIFFXMP, b"II*\x00" + b"\x00" * 8),
    ],
)
def test_unimplemented_handlers_raise(handler_cls, payload: bytes) -> None:
    embedder = EmbedXMP(handlers=[handler_cls], eager_import=False)
    signer = EmbedSigner(embedder=embedder)
    path_hint = None
    if handler_cls is MP4XMP:
        path_hint = "example.mp4"
    with pytest.raises(NotImplementedError):
        signer.embed_bytes(
            payload,
            "<x:xmpmeta><rdf:RDF/></x:xmpmeta>",
            path=path_hint,
        )


def test_supported_handler_names(embed_signer_all: EmbedSigner) -> None:
    names = embed_signer_all.supported_embed_handlers()
    assert set(names) == {"GIFXMP", "JPEGXMP", "PNGXMP", "SVGXMP", "WebPXMP"}


def test_file_round_trip(tmp_path, embed_signer_all: EmbedSigner) -> None:
    payload = _minimal_png()
    file_path = tmp_path / "image.png"
    file_path.write_bytes(payload)
    xmp = "<x:xmpmeta><rdf:RDF/></x:xmpmeta>"

    embed_signer_all.embed_file(file_path, xmp)
    assert embed_signer_all.read_xmp_file(file_path) == xmp

    embed_signer_all.remove_xmp_file(file_path, write_back=True)
    assert embed_signer_all.read_xmp_file(file_path) is None
