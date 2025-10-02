import pytest

from ._helpers import (
    async_chunks,
    build_media_signer_with_rsa,
    cms_key_entry,
    digest,
    pdf_sign_opts,
    pdf_trust_opts,
)


@pytest.fixture
async def pdf_context():
    signer, _provider, key_ref = await build_media_signer_with_rsa("pdf-test")
    return signer, cms_key_entry(key_ref), pdf_trust_opts(key_ref)


@pytest.mark.asyncio
async def test_media_signer_pdf_attached_bytes(pdf_context):
    signer, key_entry, trust_opts = pdf_context
    payload = b"pdf attached payload"

    signatures = await signer.sign_bytes(
        "pdf", key_entry, payload, opts=pdf_sign_opts(True)
    )

    assert signatures and signatures[0].mode == "attached"
    assert signatures[0].meta.get("attached") is True
    assert await signer.verify_bytes("pdf", payload, signatures, opts=trust_opts)


@pytest.mark.asyncio
async def test_media_signer_pdf_detached_bytes(pdf_context):
    signer, key_entry, trust_opts = pdf_context
    payload = b"pdf detached payload"

    signatures = await signer.sign_bytes(
        "pdf", key_entry, payload, opts=pdf_sign_opts(False)
    )

    assert signatures and signatures[0].mode == "detached"
    assert signatures[0].meta.get("attached") is False
    assert await signer.verify_bytes("pdf", payload, signatures, opts=trust_opts)


@pytest.mark.asyncio
async def test_media_signer_pdf_detached_digest(pdf_context):
    signer, key_entry, trust_opts = pdf_context
    payload = b"pdf digest payload"
    sha = digest(payload)

    signatures = await signer.sign_digest(
        "pdf", key_entry, sha, opts=pdf_sign_opts(False)
    )

    assert signatures and signatures[0].meta.get("payload_kind") == "digest"
    assert await signer.verify_digest("pdf", sha, signatures, opts=trust_opts)


@pytest.mark.asyncio
async def test_media_signer_pdf_attached_stream(pdf_context):
    signer, key_entry, trust_opts = pdf_context
    payload = b"pdf stream payload"
    stream_factory = async_chunks(payload, size=9)

    signatures = await signer.sign_stream(
        "pdf", key_entry, stream_factory(), opts=pdf_sign_opts(True)
    )

    assert signatures and signatures[0].meta.get("payload_kind") == "stream"
    assert await signer.verify_stream(
        "pdf", stream_factory(), signatures, opts=trust_opts
    )


@pytest.mark.asyncio
async def test_media_signer_pdf_detached_envelope(pdf_context):
    signer, key_entry, trust_opts = pdf_context
    envelope = {"pdf": {"title": "MediaSigner"}, "data": "payload"}

    signatures = await signer.sign_envelope(
        "pdf", key_entry, envelope, canon="json", opts=pdf_sign_opts(False)
    )

    assert signatures and signatures[0].meta.get("attached") is False
    assert await signer.verify_envelope(
        "pdf", envelope, signatures, canon="json", opts=trust_opts
    )
