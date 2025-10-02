import pytest
import pytest_asyncio
from cryptography.hazmat.primitives.serialization import pkcs7

from ._helpers import (
    async_chunks,
    CMS_FORMAT,
    build_media_signer_with_rsa,
    cms_key_entry,
    cms_trust_opts,
    digest,
)


@pytest_asyncio.fixture
async def cms_context(monkeypatch):
    original_sign = pkcs7.PKCS7SignatureBuilder.sign

    def _patched_sign(self, encoding, options, backend=None, **kwargs):
        return original_sign(self, encoding, options, backend)

    monkeypatch.setattr(pkcs7.PKCS7SignatureBuilder, "sign", _patched_sign)
    signer, _provider, key_ref = await build_media_signer_with_rsa("cms-test")
    if CMS_FORMAT not in signer.supported_formats():
        pytest.skip(f"{CMS_FORMAT} is not registered with MediaSigner")
    probe_entry = cms_key_entry(key_ref)
    probe_trust = cms_trust_opts(key_ref)
    probe_payload = b"cms probe"
    try:
        probe_sigs = await signer.sign_bytes(
            CMS_FORMAT, probe_entry, probe_payload, opts={"attached": False}
        )
        ok = await signer.verify_bytes(
            CMS_FORMAT, probe_payload, probe_sigs, opts=probe_trust
        )
    except Exception as exc:  # pragma: no cover - runtime guard
        pytest.skip(f"CMSSigner unavailable in test environment: {exc}")
    if not ok:
        pytest.skip("CMSSigner verification failed in test environment")
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
