"""Integration tests for the CMS signer via the MediaSigner facade."""

from __future__ import annotations

import pytest

from .helpers import (
    build_rsa_cert_bundle,
    chunk_payload,
    sample_json_envelope,
    sha256_digest,
)


@pytest.mark.asyncio()
async def test_media_signer_cms_sign_verify_bytes_attached() -> None:
    signer, key_entry, cert_pem = await build_rsa_cert_bundle("cms-bytes-attached")
    payload = b"cms-bytes-attached"

    signatures = await signer.sign_bytes(
        "cms", key_entry, payload, opts={"attached": True}
    )

    assert signatures and signatures[0].mode == "attached"
    assert await signer.verify_bytes(
        "cms", payload, signatures, opts={"trusted_certs": [cert_pem]}
    )


@pytest.mark.asyncio()
async def test_media_signer_cms_sign_verify_bytes_detached() -> None:
    signer, key_entry, cert_pem = await build_rsa_cert_bundle("cms-bytes-detached")
    payload = b"cms-bytes-detached"

    signatures = await signer.sign_bytes(
        "cms", key_entry, payload, opts={"attached": False}
    )

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_bytes(
        "cms", payload, signatures, opts={"trusted_certs": [cert_pem]}
    )


@pytest.mark.asyncio()
async def test_media_signer_cms_sign_verify_digest_attached() -> None:
    signer, key_entry, cert_pem = await build_rsa_cert_bundle("cms-digest-attached")
    payload = b"cms-digest-attached"
    digest = sha256_digest(payload)

    signatures = await signer.sign_digest(
        "cms", key_entry, digest, opts={"attached": True}
    )

    assert signatures and signatures[0].mode == "attached"
    assert await signer.verify_digest(
        "cms", digest, signatures, opts={"trusted_certs": [cert_pem]}
    )


@pytest.mark.asyncio()
async def test_media_signer_cms_sign_verify_digest_detached() -> None:
    signer, key_entry, cert_pem = await build_rsa_cert_bundle("cms-digest-detached")
    payload = b"cms-digest-detached"
    digest = sha256_digest(payload)

    signatures = await signer.sign_digest(
        "cms", key_entry, digest, opts={"attached": False}
    )

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_digest(
        "cms", digest, signatures, opts={"trusted_certs": [cert_pem]}
    )


@pytest.mark.asyncio()
async def test_media_signer_cms_sign_verify_stream_attached() -> None:
    signer, key_entry, cert_pem = await build_rsa_cert_bundle("cms-stream-attached")
    payload = b"cms-stream-attached"
    chunks = chunk_payload(payload)

    signatures = await signer.sign_stream(
        "cms", key_entry, chunks, opts={"attached": True}
    )

    assert signatures and signatures[0].mode == "attached"
    assert await signer.verify_stream(
        "cms", chunks, signatures, opts={"trusted_certs": [cert_pem]}
    )


@pytest.mark.asyncio()
async def test_media_signer_cms_sign_verify_stream_detached() -> None:
    signer, key_entry, cert_pem = await build_rsa_cert_bundle("cms-stream-detached")
    payload = b"cms-stream-detached"
    chunks = chunk_payload(payload)

    signatures = await signer.sign_stream(
        "cms", key_entry, chunks, opts={"attached": False}
    )

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_stream(
        "cms", chunks, signatures, opts={"trusted_certs": [cert_pem]}
    )


@pytest.mark.asyncio()
async def test_media_signer_cms_sign_verify_envelope_attached() -> None:
    signer, key_entry, cert_pem = await build_rsa_cert_bundle("cms-envelope-attached")
    envelope = sample_json_envelope("cms-envelope-attached")

    signatures = await signer.sign_envelope(
        "cms", key_entry, envelope, canon="json", opts={"attached": True}
    )

    assert signatures and signatures[0].mode == "attached"
    assert await signer.verify_envelope(
        "cms",
        envelope,
        signatures,
        canon="json",
        opts={"trusted_certs": [cert_pem]},
    )


@pytest.mark.asyncio()
async def test_media_signer_cms_sign_verify_envelope_detached() -> None:
    signer, key_entry, cert_pem = await build_rsa_cert_bundle("cms-envelope-detached")
    envelope = sample_json_envelope("cms-envelope-detached")

    signatures = await signer.sign_envelope(
        "cms", key_entry, envelope, canon="json", opts={"attached": False}
    )

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_envelope(
        "cms",
        envelope,
        signatures,
        canon="json",
        opts={"trusted_certs": [cert_pem]},
    )
