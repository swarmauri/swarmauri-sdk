from uuid import UUID

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_signing_dpop import DpopSigner


@pytest.mark.asyncio
async def test_mark_hook_called_with_jti_and_ttl() -> None:
    priv = ed25519.Ed25519PrivateKey.generate()
    pem = priv.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    signer = DpopSigner()
    sigs = await signer.sign_bytes(
        {"kind": "pem", "priv": pem, "alg": "EdDSA"},
        b"",
        opts={"htm": "GET", "htu": "https://api.example/x"},
    )
    calls: list[tuple[str, int]] = []

    def seen(_jti: str) -> bool:
        return False

    def mark(jti: str, ttl_s: int) -> None:
        calls.append((jti, ttl_s))

    assert await signer.verify_bytes(
        b"",
        sigs,
        require={
            "htm": "GET",
            "htu": "https://api.example/x",
            "replay": {"seen": seen, "mark": mark},
        },
    )
    assert calls
    jti, ttl = calls[0]
    assert isinstance(UUID(jti), UUID)
    assert ttl == 300


@pytest.mark.asyncio
async def test_seen_hook_prevents_replay() -> None:
    priv = ed25519.Ed25519PrivateKey.generate()
    pem = priv.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    signer = DpopSigner()
    sigs = await signer.sign_bytes(
        {"kind": "pem", "priv": pem, "alg": "EdDSA"},
        b"",
        opts={"htm": "POST", "htu": "https://api.example/y"},
    )
    seen_jtis: set[str] = set()

    def seen(jti: str) -> bool:
        return jti in seen_jtis

    def mark(jti: str, ttl_s: int) -> None:
        seen_jtis.add(jti)

    assert await signer.verify_bytes(
        b"",
        sigs,
        require={
            "htm": "POST",
            "htu": "https://api.example/y",
            "replay": {"seen": seen, "mark": mark},
        },
    )
    assert not await signer.verify_bytes(
        b"",
        sigs,
        require={
            "htm": "POST",
            "htu": "https://api.example/y",
            "replay": {"seen": seen, "mark": mark},
        },
    )
