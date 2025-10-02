import pytest
import pytest_asyncio

from ._helpers import (
    async_chunks,
    XMLD_FORMAT,
    build_media_signer_with_rsa,
    digest,
    xml_key_entry,
    xml_verify_opts,
)


@pytest_asyncio.fixture
async def xmld_context():
    signer, _provider, key_ref = await build_media_signer_with_rsa("xmld-test")
    if XMLD_FORMAT not in signer.supported_formats():
        pytest.skip(f"{XMLD_FORMAT} is not registered with MediaSigner")
    return signer, xml_key_entry(key_ref), xml_verify_opts(key_ref)


@pytest.mark.asyncio
async def test_media_signer_xmld_detached_bytes(xmld_context):
    signer, key_entry, verify_opts = xmld_context
    payload = b"<root>bytes</root>"

    signatures = await signer.sign_bytes(XMLD_FORMAT, key_entry, payload)

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_bytes(XMLD_FORMAT, payload, signatures, opts=verify_opts)


@pytest.mark.asyncio
async def test_media_signer_xmld_detached_digest(xmld_context):
    signer, key_entry, verify_opts = xmld_context
    payload = b"<root>digest</root>"
    sha = digest(payload)

    signatures = await signer.sign_digest(XMLD_FORMAT, key_entry, sha)

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_digest(XMLD_FORMAT, sha, signatures, opts=verify_opts)


@pytest.mark.asyncio
async def test_media_signer_xmld_detached_stream(xmld_context):
    signer, key_entry, verify_opts = xmld_context
    payload = b"<root>stream</root>"
    stream_factory = async_chunks(payload, size=5)

    signatures = await signer.sign_stream(XMLD_FORMAT, key_entry, stream_factory())

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_stream(
        XMLD_FORMAT, stream_factory(), signatures, opts=verify_opts
    )


@pytest.mark.asyncio
async def test_media_signer_xmld_detached_envelope(xmld_context):
    signer, key_entry, verify_opts = xmld_context
    envelope = "<root><value>envelope</value></root>"

    signatures = await signer.sign_envelope(
        XMLD_FORMAT, key_entry, envelope, canon="c14n"
    )

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_envelope(
        XMLD_FORMAT, envelope, signatures, canon="c14n", opts=verify_opts
    )
