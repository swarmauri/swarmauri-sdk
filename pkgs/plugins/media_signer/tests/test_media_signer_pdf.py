import pytest
import pytest_asyncio

from ._helpers import (
    async_chunks,
    PDF_FORMAT,
    build_media_signer_with_rsa,
    cms_key_entry,
    digest,
    pdf_sign_opts,
    pdf_trust_opts,
)


@pytest_asyncio.fixture
async def pdf_context():
    signer, _provider, key_ref = await build_media_signer_with_rsa("pdf-test")
    if PDF_FORMAT not in signer.supported_formats():
        pytest.skip(f"{PDF_FORMAT} is not registered with MediaSigner")
    return signer, cms_key_entry(key_ref), pdf_trust_opts(key_ref)


@pytest.mark.asyncio
async def test_media_signer_pdf_attached_bytes(pdf_context):
    signer, key_entry, trust_opts = pdf_context
    payload = b"pdf attached payload"

    signatures = await signer.sign_bytes(
        PDF_FORMAT, key_entry, payload, opts=pdf_sign_opts(True)
    )

    assert signatures and signatures[0].mode == "attached"
    assert signatures[0].meta.get("attached") is True
    assert await signer.verify_bytes(PDF_FORMAT, payload, signatures, opts=trust_opts)


@pytest.mark.asyncio
async def test_media_signer_pdf_detached_bytes(pdf_context):
    signer, key_entry, trust_opts = pdf_context
    payload = b"pdf detached payload"

    signatures = await signer.sign_bytes(
        PDF_FORMAT, key_entry, payload, opts=pdf_sign_opts(False)
    )

    assert signatures and signatures[0].mode == "detached"
    assert signatures[0].meta.get("attached") is False
    assert await signer.verify_bytes(PDF_FORMAT, payload, signatures, opts=trust_opts)


@pytest.mark.asyncio
async def test_media_signer_pdf_detached_digest(pdf_context):
    signer, key_entry, trust_opts = pdf_context
    payload = b"pdf digest payload"
    sha = digest(payload)

    signatures = await signer.sign_digest(
        PDF_FORMAT, key_entry, sha, opts=pdf_sign_opts(False)
    )

    assert signatures and signatures[0].meta.get("payload_kind") == "digest"
    assert await signer.verify_digest(PDF_FORMAT, sha, signatures, opts=trust_opts)


@pytest.mark.asyncio
async def test_media_signer_pdf_attached_stream(pdf_context):
    signer, key_entry, trust_opts = pdf_context
    payload = b"pdf stream payload"
    stream_factory = async_chunks(payload, size=9)

    signatures = await signer.sign_stream(
        PDF_FORMAT, key_entry, stream_factory(), opts=pdf_sign_opts(True)
    )

    assert signatures and signatures[0].meta.get("payload_kind") == "stream"
    assert await signer.verify_stream(
        PDF_FORMAT, stream_factory(), signatures, opts=trust_opts
    )


@pytest.mark.asyncio
async def test_media_signer_pdf_detached_envelope(pdf_context):
    signer, key_entry, trust_opts = pdf_context
    envelope = {"pdf": {"title": "MediaSigner"}, "data": "payload"}

    signatures = await signer.sign_envelope(
        PDF_FORMAT, key_entry, envelope, canon="json", opts=pdf_sign_opts(False)
    )

    assert signatures and signatures[0].meta.get("attached") is False
    assert await signer.verify_envelope(
        PDF_FORMAT, envelope, signatures, canon="json", opts=trust_opts
    )
