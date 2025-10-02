"""Integration tests for the PDF signer through MediaSigner."""

from __future__ import annotations

import pytest

from .helpers import (
    build_pdf_signer,
    chunk_payload,
    sample_pdf_bytes,
    sha256_digest,
)


@pytest.mark.asyncio()
async def test_media_signer_pdf_sign_verify_bytes_attached() -> None:
    signer, key_entry, cert_pem = await build_pdf_signer("pdf-bytes-attached")
    payload = sample_pdf_bytes("pdf-bytes-attached")

    signatures = await signer.sign_bytes(
        "pdf", key_entry, payload, opts={"attached": True}
    )

    assert signatures and signatures[0].mode == "attached"
    assert await signer.verify_bytes(
        "pdf", payload, signatures, opts={"trusted_certs": [cert_pem]}
    )


@pytest.mark.asyncio()
async def test_media_signer_pdf_sign_verify_bytes_detached() -> None:
    signer, key_entry, cert_pem = await build_pdf_signer("pdf-bytes-detached")
    payload = sample_pdf_bytes("pdf-bytes-detached")

    signatures = await signer.sign_bytes(
        "pdf", key_entry, payload, opts={"attached": False}
    )

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_bytes(
        "pdf", payload, signatures, opts={"trusted_certs": [cert_pem]}
    )


@pytest.mark.asyncio()
async def test_media_signer_pdf_sign_verify_digest_attached() -> None:
    signer, key_entry, cert_pem = await build_pdf_signer("pdf-digest-attached")
    payload = sample_pdf_bytes("pdf-digest-attached")
    digest = sha256_digest(payload)

    signatures = await signer.sign_digest(
        "pdf", key_entry, digest, opts={"attached": True}
    )

    assert signatures and signatures[0].mode == "attached"
    assert await signer.verify_digest(
        "pdf", digest, signatures, opts={"trusted_certs": [cert_pem]}
    )


@pytest.mark.asyncio()
async def test_media_signer_pdf_sign_verify_digest_detached() -> None:
    signer, key_entry, cert_pem = await build_pdf_signer("pdf-digest-detached")
    payload = sample_pdf_bytes("pdf-digest-detached")
    digest = sha256_digest(payload)

    signatures = await signer.sign_digest(
        "pdf", key_entry, digest, opts={"attached": False}
    )

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_digest(
        "pdf", digest, signatures, opts={"trusted_certs": [cert_pem]}
    )


@pytest.mark.asyncio()
async def test_media_signer_pdf_sign_verify_stream_attached() -> None:
    signer, key_entry, cert_pem = await build_pdf_signer("pdf-stream-attached")
    payload = sample_pdf_bytes("pdf-stream-attached")
    chunks = chunk_payload(payload)

    signatures = await signer.sign_stream(
        "pdf", key_entry, chunks, opts={"attached": True}
    )

    assert signatures and signatures[0].mode == "attached"
    assert await signer.verify_stream(
        "pdf", chunks, signatures, opts={"trusted_certs": [cert_pem]}
    )


@pytest.mark.asyncio()
async def test_media_signer_pdf_sign_verify_stream_detached() -> None:
    signer, key_entry, cert_pem = await build_pdf_signer("pdf-stream-detached")
    payload = sample_pdf_bytes("pdf-stream-detached")
    chunks = chunk_payload(payload)

    signatures = await signer.sign_stream(
        "pdf", key_entry, chunks, opts={"attached": False}
    )

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_stream(
        "pdf", chunks, signatures, opts={"trusted_certs": [cert_pem]}
    )


@pytest.mark.asyncio()
async def test_media_signer_pdf_sign_verify_envelope_attached() -> None:
    signer, key_entry, cert_pem = await build_pdf_signer("pdf-envelope-attached")
    envelope = sample_pdf_bytes("pdf-envelope-attached")

    signatures = await signer.sign_envelope(
        "pdf", key_entry, envelope, canon="pdf", opts={"attached": True}
    )

    assert signatures and signatures[0].mode == "attached"
    assert await signer.verify_envelope(
        "pdf",
        envelope,
        signatures,
        canon="pdf",
        opts={"trusted_certs": [cert_pem]},
    )


@pytest.mark.asyncio()
async def test_media_signer_pdf_sign_verify_envelope_detached() -> None:
    signer, key_entry, cert_pem = await build_pdf_signer("pdf-envelope-detached")
    envelope = sample_pdf_bytes("pdf-envelope-detached")

    signatures = await signer.sign_envelope(
        "pdf", key_entry, envelope, canon="pdf", opts={"attached": False}
    )

    assert signatures and signatures[0].mode == "detached"
    assert await signer.verify_envelope(
        "pdf",
        envelope,
        signatures,
        canon="pdf",
        opts={"trusted_certs": [cert_pem]},
    )
