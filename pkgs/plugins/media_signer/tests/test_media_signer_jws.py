import pytest
import pytest_asyncio

from ._helpers import (
    async_chunks,
    JWS_FORMAT,
    build_media_signer_with_hmac,
    digest,
    jws_hmac_key,
    jws_verify_opts,
)


@pytest_asyncio.fixture
async def jws_context():
    signer, _provider, key_ref = await build_media_signer_with_hmac("jws-test")
    if JWS_FORMAT not in signer.supported_formats():
        pytest.skip(f"{JWS_FORMAT} is not registered with MediaSigner")
    return signer, jws_hmac_key(key_ref), jws_verify_opts(key_ref)


@pytest.mark.asyncio
async def test_media_signer_jws_attached_bytes(jws_context):
    signer, key_entry, verify_opts = jws_context
    payload = b"jws attached payload"

    signatures = await signer.sign_bytes(
        JWS_FORMAT, key_entry, payload, opts={"alg": "HS256"}
    )

    assert signatures and signatures[0].mode == "attached"
    assert await signer.verify_bytes(JWS_FORMAT, payload, signatures, opts=verify_opts)


@pytest.mark.asyncio
async def test_media_signer_jws_digest_round_trip(jws_context):
    signer, key_entry, verify_opts = jws_context
    payload = b"jws digest payload"
    sha = digest(payload)

    signatures = await signer.sign_digest(
        JWS_FORMAT, key_entry, sha, opts={"alg": "HS256"}
    )

    assert signatures and signatures[0].meta.get("payload_kind") == "digest"
    assert await signer.verify_digest(JWS_FORMAT, sha, signatures, opts=verify_opts)


@pytest.mark.asyncio
async def test_media_signer_jws_stream_round_trip(jws_context):
    signer, key_entry, verify_opts = jws_context
    payload = b"jws stream payload"
    stream_factory = async_chunks(payload, size=6)

    signatures = await signer.sign_stream(
        JWS_FORMAT, key_entry, stream_factory(), opts={"alg": "HS256"}
    )

    assert signatures and signatures[0].meta.get("payload_kind") == "stream"
    assert await signer.verify_stream(
        JWS_FORMAT, stream_factory(), signatures, opts=verify_opts
    )


@pytest.mark.asyncio
async def test_media_signer_jws_envelope_round_trip(jws_context):
    signer, key_entry, verify_opts = jws_context
    envelope = {"type": "jws-envelope", "version": 1}

    signatures = await signer.sign_envelope(
        JWS_FORMAT, key_entry, envelope, canon="json", opts={"alg": "HS256"}
    )

    assert signatures and signatures[0].meta.get("payload_kind") == "envelope"
    assert await signer.verify_envelope(
        JWS_FORMAT, envelope, signatures, canon="json", opts=verify_opts
    )
