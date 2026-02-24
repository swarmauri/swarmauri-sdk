import hashlib

import pytest

pytestmark = pytest.mark.asyncio


def _hash_email(email: str) -> str:
    return hashlib.sha1(email.lower().encode("utf-8")).hexdigest()


async def test_legacy_index_machine_readable_headers(seeded_client, sample_key):
    resp = await seeded_client.get(
        "/pks/lookup",
        params={"op": "index", "search": sample_key.email, "options": "mr"},
    )
    assert resp.status_code == 200
    assert resp.headers.get("Access-Control-Allow-Origin") == "*"
    assert resp.headers.get("Content-Type", "").startswith("text/plain")
    body = resp.text
    assert "info:" in body and "pub:" in body


async def test_legacy_get_returns_ascii_armored(seeded_client, sample_key):
    resp = await seeded_client.get(
        "/pks/lookup",
        params={"op": "get", "search": f"0x{sample_key.fingerprint}"},
    )
    assert resp.status_code == 200
    assert resp.headers.get("Access-Control-Allow-Origin") == "*"
    ctype = resp.headers.get("Content-Type", "")
    assert ctype.startswith("application/pgp-keys")
    assert "-----BEGIN PGP PUBLIC KEY BLOCK-----" in resp.text


async def test_legacy_hget_uses_email_hash(seeded_client, sample_key):
    resp = await seeded_client.get(
        "/pks/lookup",
        params={"op": "hget", "search": _hash_email(sample_key.email)},
    )
    assert resp.status_code == 200
    assert resp.headers.get("Access-Control-Allow-Origin") == "*"
    assert resp.text.startswith("-----BEGIN PGP PUBLIC KEY BLOCK-----")


async def test_legacy_rejects_short_keyid(seeded_client):
    resp = await seeded_client.get(
        "/pks/lookup",
        params={"op": "get", "search": "0xDEADBEEF"},
    )
    assert resp.status_code == 404
