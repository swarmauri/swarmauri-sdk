"""Integration tests covering the JWS signer via MediaSigner."""

from __future__ import annotations

import pytest

from swarmauri_core.signing.types import Signature

from .helpers import (
    build_jws_material,
    chunk_payload,
    sample_json_envelope,
    sha256_digest,
)


@pytest.mark.asyncio()
async def test_media_signer_jws_sign_verify_bytes_attached() -> None:
    signer, key_entry, verify_opts = await build_jws_material("jws-bytes-attached")
    payload = b"jws-bytes-attached"

    signatures = await signer.sign_bytes("jws", key_entry, payload)

    assert signatures and signatures[0].mode == "attached"
    assert await signer.verify_bytes("jws", payload, signatures, opts=verify_opts)


@pytest.mark.asyncio()
async def test_media_signer_jws_verify_bytes_detached_mode() -> None:
    signer, key_entry, verify_opts = await build_jws_material("jws-bytes-detached")
    payload = b"jws-bytes-detached"

    signatures = await signer.sign_bytes("jws", key_entry, payload)
    base = signatures[0]
    detached = [
        Signature(
            kid=base.kid,
            version=base.version,
            format=base.format,
            mode="detached",
            alg=base.alg,
            artifact=base.artifact,
            headers=base.headers,
            meta=base.meta,
        )
    ]

    assert await signer.verify_bytes("jws", payload, detached, opts=verify_opts)


@pytest.mark.asyncio()
async def test_media_signer_jws_sign_verify_digest_attached() -> None:
    signer, key_entry, verify_opts = await build_jws_material("jws-digest-attached")
    payload = b"jws-digest-attached"
    digest = sha256_digest(payload)

    signatures = await signer.sign_digest("jws", key_entry, digest)

    assert signatures and signatures[0].mode == "attached"
    assert await signer.verify_digest("jws", digest, signatures, opts=verify_opts)


@pytest.mark.asyncio()
async def test_media_signer_jws_verify_digest_detached_mode() -> None:
    signer, key_entry, verify_opts = await build_jws_material("jws-digest-detached")
    payload = b"jws-digest-detached"
    digest = sha256_digest(payload)

    signatures = await signer.sign_digest("jws", key_entry, digest)
    base = signatures[0]
    detached = [
        Signature(
            kid=base.kid,
            version=base.version,
            format=base.format,
            mode="detached",
            alg=base.alg,
            artifact=base.artifact,
            headers=base.headers,
            meta=base.meta,
        )
    ]

    assert await signer.verify_digest("jws", digest, detached, opts=verify_opts)


@pytest.mark.asyncio()
async def test_media_signer_jws_sign_verify_stream_attached() -> None:
    signer, key_entry, verify_opts = await build_jws_material("jws-stream-attached")
    payload = b"jws-stream-attached"
    chunks = chunk_payload(payload)

    signatures = await signer.sign_stream("jws", key_entry, chunks)

    assert signatures and signatures[0].mode == "attached"
    assert await signer.verify_stream("jws", chunks, signatures, opts=verify_opts)


@pytest.mark.asyncio()
async def test_media_signer_jws_verify_stream_detached_mode() -> None:
    signer, key_entry, verify_opts = await build_jws_material("jws-stream-detached")
    payload = b"jws-stream-detached"
    chunks = chunk_payload(payload)

    signatures = await signer.sign_stream("jws", key_entry, chunks)
    base = signatures[0]
    detached = [
        Signature(
            kid=base.kid,
            version=base.version,
            format=base.format,
            mode="detached",
            alg=base.alg,
            artifact=base.artifact,
            headers=base.headers,
            meta=base.meta,
        )
    ]

    assert await signer.verify_stream("jws", chunks, detached, opts=verify_opts)


@pytest.mark.asyncio()
async def test_media_signer_jws_sign_verify_envelope_attached() -> None:
    signer, key_entry, verify_opts = await build_jws_material("jws-envelope-attached")
    envelope = sample_json_envelope("jws-envelope-attached")

    signatures = await signer.sign_envelope("jws", key_entry, envelope, canon="json")

    assert signatures and signatures[0].mode == "attached"
    assert await signer.verify_envelope(
        "jws", envelope, signatures, canon="json", opts=verify_opts
    )


@pytest.mark.asyncio()
async def test_media_signer_jws_verify_envelope_detached_mode() -> None:
    signer, key_entry, verify_opts = await build_jws_material("jws-envelope-detached")
    envelope = sample_json_envelope("jws-envelope-detached")

    signatures = await signer.sign_envelope("jws", key_entry, envelope, canon="json")
    base = signatures[0]
    detached = [
        Signature(
            kid=base.kid,
            version=base.version,
            format=base.format,
            mode="detached",
            alg=base.alg,
            artifact=base.artifact,
            headers=base.headers,
            meta=base.meta,
        )
    ]

    assert await signer.verify_envelope(
        "jws", envelope, detached, canon="json", opts=verify_opts
    )
