import pytest
import pytest_asyncio

pytest.importorskip("pgpy")

from ._helpers import (
    OPENPGP_FORMAT,
    async_chunks,
    build_media_signer_with_openpgp,
    digest,
    openpgp_private_entry,
    openpgp_verify_opts,
)


@pytest_asyncio.fixture
async def openpgp_context():
    signer, _provider, key_ref = await build_media_signer_with_openpgp("openpgp-test")
    return signer, openpgp_private_entry(key_ref), openpgp_verify_opts(key_ref)


@pytest.mark.asyncio
async def test_media_signer_openpgp_detached_bytes(openpgp_context):
    signer, key_entry, verify_opts = openpgp_context
    payload = b"openpgp bytes payload"

    signatures = await signer.sign_bytes(OPENPGP_FORMAT, key_entry, payload)

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_bytes(
        OPENPGP_FORMAT, payload, signatures, opts=verify_opts
    )


@pytest.mark.asyncio
async def test_media_signer_openpgp_detached_digest(openpgp_context):
    signer, key_entry, verify_opts = openpgp_context
    payload = b"openpgp digest payload"
    sha = digest(payload)

    signatures = await signer.sign_digest(OPENPGP_FORMAT, key_entry, sha)

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_digest(OPENPGP_FORMAT, sha, signatures, opts=verify_opts)


@pytest.mark.asyncio
async def test_media_signer_openpgp_detached_stream(openpgp_context):
    signer, key_entry, verify_opts = openpgp_context
    payload = b"openpgp stream payload"
    stream_factory = async_chunks(payload, size=8)

    signatures = await signer.sign_stream(OPENPGP_FORMAT, key_entry, stream_factory())

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_stream(
        OPENPGP_FORMAT, stream_factory(), signatures, opts=verify_opts
    )


@pytest.mark.asyncio
async def test_media_signer_openpgp_detached_envelope(openpgp_context):
    signer, key_entry, verify_opts = openpgp_context
    envelope = {"event": "openpgp", "status": "ok"}

    signatures = await signer.sign_envelope(
        OPENPGP_FORMAT, key_entry, envelope, canon="json"
    )

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_envelope(
        OPENPGP_FORMAT, envelope, signatures, canon="json", opts=verify_opts
    )
