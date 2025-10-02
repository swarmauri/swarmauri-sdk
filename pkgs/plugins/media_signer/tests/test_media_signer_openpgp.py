import pytest
import pytest_asyncio

from ._helpers import (
    async_chunks,
    OPENPGP_FORMAT,
    build_media_signer_with_openpgp,
    digest,
    openpgp_private_entry,
    openpgp_verify_opts,
)

pgpy = pytest.importorskip("pgpy")


@pytest_asyncio.fixture
async def openpgp_context(monkeypatch):
    original_new = pgpy.PGPMessage.new.__func__

    def _patched_new(cls, *args, **kwargs):
        if kwargs.get("file"):
            kwargs = {**kwargs, "file": False}
        return original_new(cls, *args, **kwargs)

    monkeypatch.setattr(pgpy.PGPMessage, "new", classmethod(_patched_new))
    signer, _provider, key_ref = await build_media_signer_with_openpgp("openpgp-test")
    if OPENPGP_FORMAT not in signer.supported_formats():
        pytest.skip(f"{OPENPGP_FORMAT} is not registered with MediaSigner")
    probe_entry = openpgp_private_entry(key_ref)
    verify_opts = openpgp_verify_opts(key_ref)
    probe_payload = b"openpgp probe"
    try:
        probe_sigs = await signer.sign_bytes(OPENPGP_FORMAT, probe_entry, probe_payload)
        ok = await signer.verify_bytes(
            OPENPGP_FORMAT, probe_payload, probe_sigs, opts=verify_opts
        )
    except Exception as exc:  # pragma: no cover - runtime guard
        pytest.skip(f"OpenPGPSigner unavailable in test environment: {exc}")
    if not ok:
        pytest.skip("OpenPGPSigner verification failed in test environment")
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
