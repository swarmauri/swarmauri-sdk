import pytest
import pytest_asyncio

from ._helpers import (
    CMS_FORMAT,
    async_chunks,
    build_media_signer_with_rsa,
    cms_key_entry,
    cms_trust_opts,
    digest,
)


@pytest_asyncio.fixture
async def cms_context():
    signer, _provider, key_ref = await build_media_signer_with_rsa("cms-test")
    return signer, cms_key_entry(key_ref), cms_trust_opts(key_ref)


@pytest.mark.asyncio
async def test_media_signer_cms_attached_bytes(cms_context):
    signer, key_entry, trust_opts = cms_context
    payload = b"cms attached payload"

    signatures = await signer.sign_bytes(
        CMS_FORMAT, key_entry, payload, opts={"attached": True}
    )

    assert signatures and signatures[0].mode == "attached"
    assert await signer.verify_bytes(CMS_FORMAT, payload, signatures, opts=trust_opts)


@pytest.mark.asyncio
async def test_media_signer_cms_detached_bytes(cms_context):
    signer, key_entry, trust_opts = cms_context
    payload = b"cms detached payload"

    signatures = await signer.sign_bytes(
        CMS_FORMAT, key_entry, payload, opts={"attached": False}
    )

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_bytes(CMS_FORMAT, payload, signatures, opts=trust_opts)


@pytest.mark.asyncio
async def test_media_signer_cms_detached_digest(cms_context):
    signer, key_entry, trust_opts = cms_context
    payload = b"cms digest payload"
    sha = digest(payload)

    signatures = await signer.sign_digest(
        CMS_FORMAT, key_entry, sha, opts={"attached": False}
    )

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_digest(CMS_FORMAT, sha, signatures, opts=trust_opts)


@pytest.mark.asyncio
async def test_media_signer_cms_attached_stream(cms_context):
    signer, key_entry, trust_opts = cms_context
    payload = b"cms stream payload for media signer"
    stream_factory = async_chunks(payload, size=7)

    signatures = await signer.sign_stream(
        CMS_FORMAT, key_entry, stream_factory(), opts={"attached": True}
    )

    assert signatures and signatures[0].mode == "attached"
    assert await signer.verify_stream(
        CMS_FORMAT, stream_factory(), signatures, opts=trust_opts
    )


@pytest.mark.asyncio
async def test_media_signer_cms_detached_envelope(cms_context):
    signer, key_entry, trust_opts = cms_context
    envelope = {"event": "cms-envelope", "value": 42}

    signatures = await signer.sign_envelope(
        CMS_FORMAT,
        key_entry,
        envelope,
        canon="json",
        opts={"attached": False},
    )

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_envelope(
        CMS_FORMAT,
        envelope,
        signatures,
        canon="json",
        opts=trust_opts,
    )
