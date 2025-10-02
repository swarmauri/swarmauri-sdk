"""Integration tests for the XML Digital Signature plugin through MediaSigner."""

from __future__ import annotations

import pytest

from .helpers import (
    build_xmld_signer,
    chunk_payload,
    sample_xml_document,
    sha256_digest,
)


@pytest.mark.asyncio()
async def test_media_signer_xmld_sign_verify_bytes_detached() -> None:
    signer, key_entry, pubkeys = await build_xmld_signer("xmld-bytes")
    payload = b"xmld-bytes"

    signatures = await signer.sign_bytes("xmld", key_entry, payload)

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_bytes(
        "xmld", payload, signatures, opts={"pubkeys": pubkeys}
    )


@pytest.mark.asyncio()
async def test_media_signer_xmld_sign_verify_digest_detached() -> None:
    signer, key_entry, pubkeys = await build_xmld_signer("xmld-digest")
    payload = b"xmld-digest"
    digest = sha256_digest(payload)

    signatures = await signer.sign_digest("xmld", key_entry, digest)

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_digest(
        "xmld", digest, signatures, opts={"pubkeys": pubkeys}
    )


@pytest.mark.asyncio()
async def test_media_signer_xmld_sign_verify_stream_detached() -> None:
    signer, key_entry, pubkeys = await build_xmld_signer("xmld-stream")
    payload = b"xmld-stream"
    chunks = chunk_payload(payload)

    signatures = await signer.sign_stream("xmld", key_entry, chunks)

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_stream(
        "xmld", chunks, signatures, opts={"pubkeys": pubkeys}
    )


@pytest.mark.asyncio()
async def test_media_signer_xmld_sign_verify_envelope_detached() -> None:
    signer, key_entry, pubkeys = await build_xmld_signer("xmld-envelope")
    envelope = sample_xml_document("xmld-envelope")

    signatures = await signer.sign_envelope("xmld", key_entry, envelope, canon="c14n")

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_envelope(
        "xmld", envelope, signatures, canon="c14n", opts={"pubkeys": pubkeys}
    )
