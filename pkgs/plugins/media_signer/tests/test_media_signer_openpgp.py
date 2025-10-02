"""Integration tests for the OpenPGP signer exposed by MediaSigner."""

from __future__ import annotations

import pytest

from .helpers import (
    build_openpgp_material,
    chunk_payload,
    sample_json_envelope,
    sha256_digest,
)


@pytest.mark.asyncio()
async def test_media_signer_openpgp_sign_verify_bytes_detached() -> None:
    signer, key_entry, public_entries = await build_openpgp_material("openpgp-bytes")
    payload = b"openpgp-bytes"

    signatures = await signer.sign_bytes("openpgp", key_entry, payload)

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_bytes(
        "openpgp", payload, signatures, opts={"pubkeys": public_entries}
    )


@pytest.mark.asyncio()
async def test_media_signer_openpgp_sign_verify_digest_detached() -> None:
    signer, key_entry, public_entries = await build_openpgp_material("openpgp-digest")
    payload = b"openpgp-digest"
    digest = sha256_digest(payload)

    signatures = await signer.sign_digest("openpgp", key_entry, digest)

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_digest(
        "openpgp", digest, signatures, opts={"pubkeys": public_entries}
    )


@pytest.mark.asyncio()
async def test_media_signer_openpgp_sign_verify_stream_detached() -> None:
    signer, key_entry, public_entries = await build_openpgp_material("openpgp-stream")
    payload = b"openpgp-stream"
    chunks = chunk_payload(payload)

    signatures = await signer.sign_stream("openpgp", key_entry, chunks)

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_stream(
        "openpgp", chunks, signatures, opts={"pubkeys": public_entries}
    )


@pytest.mark.asyncio()
async def test_media_signer_openpgp_sign_verify_envelope_detached() -> None:
    signer, key_entry, public_entries = await build_openpgp_material("openpgp-envelope")
    envelope = sample_json_envelope("openpgp-envelope")

    signatures = await signer.sign_envelope(
        "openpgp", key_entry, envelope, canon="json"
    )

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_envelope(
        "openpgp", envelope, signatures, canon="json", opts={"pubkeys": public_entries}
    )
