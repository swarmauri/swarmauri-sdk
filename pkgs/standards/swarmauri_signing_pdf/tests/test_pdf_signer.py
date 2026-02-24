import pytest

from swarmauri_core.signing.types import Signature
from swarmauri_signing_pdf.pdf_signer import (
    PDFSigner,
    _adapt_signature,
    _canon_json,
    _ensure_bytes,
    _pdf_meta,
)


def test_pdf_meta_defaults() -> None:
    assert _pdf_meta(None) == {"attached": True, "pdf": {}}


def test_pdf_meta_with_fields() -> None:
    opts = {
        "attached": False,
        "pdf": {"reason": "Signed", "location": None},
        "contact": "dev@example.com",
    }
    assert _pdf_meta(opts) == {
        "attached": False,
        "pdf": {"reason": "Signed", "contact": "dev@example.com"},
    }


def test_ensure_bytes_accepts_bytes() -> None:
    payload = b"pdf"
    assert _ensure_bytes(payload) == payload


def test_ensure_bytes_accepts_str() -> None:
    assert _ensure_bytes("pdf") == b"pdf"


def test_ensure_bytes_rejects_invalid_type() -> None:
    with pytest.raises(TypeError, match="PDF payloads must be bytes or str"):
        _ensure_bytes(1234)  # type: ignore[arg-type]


def test_adapt_signature_updates_meta_and_format() -> None:
    signature = Signature(
        kid="kid",
        version=1,
        format="cms",
        mode="attached",
        alg="SHA256",
        artifact=b"sig",
        meta={"existing": True},
    )
    adapted = _adapt_signature(
        signature, payload_kind="bytes", pdf_meta={"attached": True, "pdf": {}}
    )
    assert adapted.format == "pdf-cms"
    assert adapted.meta == {
        "existing": True,
        "attached": True,
        "pdf": {},
        "payload_kind": "bytes",
    }


@pytest.mark.asyncio
async def test_canonicalize_envelope_pdf_bytes() -> None:
    signer = PDFSigner()
    payload = b"%PDF"
    assert await signer.canonicalize_envelope(payload) == payload
    assert (
        await signer.canonicalize_envelope(bytearray(payload), canon="pdf") == payload
    )


@pytest.mark.asyncio
async def test_canonicalize_envelope_pdf_requires_bytes() -> None:
    signer = PDFSigner()
    with pytest.raises(TypeError, match="PDF envelopes require bytes payloads"):
        await signer.canonicalize_envelope({"a": 1})


@pytest.mark.asyncio
async def test_canonicalize_envelope_json_mapping() -> None:
    signer = PDFSigner()
    env = {"b": 2, "a": 1}
    assert await signer.canonicalize_envelope(env, canon="json") == _canon_json(env)


@pytest.mark.asyncio
async def test_canonicalize_envelope_json_requires_mapping() -> None:
    signer = PDFSigner()
    with pytest.raises(TypeError, match="json canon expects mapping envelope"):
        await signer.canonicalize_envelope(b"data", canon="json")


@pytest.mark.asyncio
async def test_canonicalize_envelope_unknown_canon() -> None:
    signer = PDFSigner()
    with pytest.raises(ValueError, match="Unsupported canon for PDFSigner"):
        await signer.canonicalize_envelope(b"data", canon="xml")
