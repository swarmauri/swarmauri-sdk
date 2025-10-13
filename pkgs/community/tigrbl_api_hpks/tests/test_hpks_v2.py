import base64
import datetime as dt
import inspect

import httpx
import pytest
from pgpy import PGPKey, PGPUID
from pgpy.constants import (
    CompressionAlgorithm,
    HashAlgorithm,
    KeyFlags,
    PubKeyAlgorithm,
    RevocationReason,
    SymmetricKeyAlgorithm,
)

from tigrbl_api_hpks.api import build_app

pytestmark = pytest.mark.asyncio


GPG_ASCII = """-----BEGIN PGP PUBLIC KEY BLOCK-----

mQENBGjteNEBCAC3kz7GoeRyKbOJUbjMcFlnljOQPMITodkHi5mHKfNvekbqrhxU
773B4SXVEQLGyQKgzvA79ENL95Ak9HjPk6Op8DuzeergIoBgq1SK18Lg8Rc3uPI/
f+ATJx6sRSSxvDR+acHNHFZL1hkaSwnr2CwWsdO4X5kMZfGDKh16GMdNIU+TQl00
WvkAcSBes8jha9YBXfZbNw4X2YI51qp1Y+gmrGWtLQ4+iodGgTQLzGvtKogMmJuZ
5Seu7zWTZiL0K2JfFfipOKYLLFqHiPku/05VrWMRc4H5Y5WTI3arot40IkcopKTU
+RCXuMsgRXuohzfCpLgySoW8g4JagfJlOIXHABEBAAG0JEhQS1MgU0RLIFRlc3Qg
PGhwa3Mtc2RrQGV4YW1wbGUuY29tPokBUgQTAQoAPBYhBASQP7RnDQ4LC90hT68D
qmkO8gvXBQJo7XjRAxsvBAULCQgHAgIiAgYVCgkICwIEFgIDAQIeBwIXgAAKCRCv
A6ppDvIL10HtB/9O9to0c9b/sj3CFqvvBVjtutaOV/4KMC8DdGVdIzPD2c/OqGzq
pMxNpIdEQZlSNcXglPckEMfKLZ3uSXVaFap4CLgrOQnIDD3lSiyvzuekGfp8Atzq
67qh2Oh+vnidNvXsWQI0lPOno9ntcfRsz1SKNR9YkmHAE/uNIYXydz0YKKbg6CKS
sdijOin15zbv+tOUHeybsinoeRd/l7Hch7aPcpJ/DxDRZ25tZ8YcqBa9R0yXO8TW
TgmuhYwS0nE7m0Ba/PBFAj0QQENj6IgkrJRvbv9eT4KMxZnl9B6mr5vGrt+wW4D6
Ic6hZKg7irQLOe8O+yFfRMQ3wrYKcq12wy6V
=1xC3
-----END PGP PUBLIC KEY BLOCK-----
"""

GPG_BINARY = base64.b64decode(
    "mQENBGjteNEBCAC3kz7GoeRyKbOJUbjMcFlnljOQPMITodkHi5mHKfNvekbqrhxU773B4SXVEQLGyQKgzvA79ENL95Ak9HjPk6Op8DuzeergIoBgq1SK18Lg8Rc3uPI/"
    "f+ATJx6sRSSxvDR+acHNHFZL1hkaSwnr2CwWsdO4X5kMZfGDKh16GMdNIU+TQl00WvkAcSBes8jha9YBXfZbNw4X2YI51qp1Y+gmrGWtLQ4+iodGgTQLzGvtKogMmJuZ"
    "5Seu7zWTZiL0K2JfFfipOKYLLFqHiPku/05VrWMRc4H5Y5WTI3arot40IkcopKTU+RCXuMsgRXuohzfCpLgySoW8g4JagfJlOIXHABEBAAG0JEhQS1MgU0RLIFRlc3Qg"
    "PGhwa3Mtc2RrQGV4YW1wbGUuY29tPokBUgQTAQoAPBYhBASQP7RnDQ4LC90hT68DqmkO8gvXBQJo7XjRAxsvBAULCQgHAgIiAgYVCgkICwIEFgIDAQIeBwIXgAAKCRCv"
    "A6ppDvIL10HtB/9O9to0c9b/sj3CFqvvBVjtutaOV/4KMC8DdGVdIzPD2c/OqGzqpMxNpIdEQZlSNcXglPckEMfKLZ3uSXVaFap4CLgrOQnIDD3lSiyvzuekGfp8Atzq"
    "67qh2Oh+vnidNvXsWQI0lPOno9ntcfRsz1SKNR9YkmHAE/uNIYXydz0YKKbg6CKSsdijOin15zbv+tOUHeybsinoeRd/l7Hch7aPcpJ/DxDRZ25tZ8YcqBa9R0yXO8TW"
    "TgmuhYwS0nE7m0Ba/PBFAj0QQENj6IgkrJRvbv9eT4KMxZnl9B6mr5vGrt+wW4D6Ic6hZKg7irQLOe8O+yFfRMQ3wrYKcq12wy6V"
)


def _make_key(email: str) -> tuple[str, bytes, str]:
    key = PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 2048)
    uid = PGPUID.new(f"HPKS Example {email}", email=email)
    key.add_uid(
        uid,
        usage={KeyFlags.Sign},
        hashes=[HashAlgorithm.SHA256],
        ciphers=[SymmetricKeyAlgorithm.AES256],
        compression=[CompressionAlgorithm.ZLIB],
    )
    fingerprint = key.fingerprint.replace(" ", "").upper()
    return str(key), bytes(key), fingerprint


async def test_v2_index_json_contract_and_cors(seeded_client, sample_key):
    resp = await seeded_client.get(f"/pks/v2/index/{sample_key.email}")
    assert resp.status_code == 200
    assert resp.headers.get("Access-Control-Allow-Origin") == "*"
    data = resp.json()
    assert isinstance(data, list)
    assert data and data[0]["fingerprint"] == sample_key.fingerprint


async def test_v2_index_marks_unrevoked_keys_active(seeded_client, sample_key):
    resp = await seeded_client.get(f"/pks/v2/index/{sample_key.fingerprint}")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload and payload[0]["revoked"] is False
    assert payload[0]["revoked_at"] is None


async def test_v2_vfpget_returns_binary_bundle(seeded_client, sample_key):
    resp = await seeded_client.get(f"/pks/v2/vfpget/{sample_key.fingerprint}")
    assert resp.status_code == 200
    assert resp.headers.get("Access-Control-Allow-Origin") == "*"
    ctype = resp.headers.get("Content-Type", "")
    assert "application/pgp-keys" in ctype and "encoding=binary" in ctype
    assert resp.content.startswith(b"-----") is False


async def test_v2_vfpget_preserves_original_gpg_bundle():
    app = build_app()
    init_result = app.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as local_client:
        resp = await local_client.post(
            "/pks/add",
            data={"keytext": GPG_ASCII},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert resp.status_code == 200

        key, _ = PGPKey.from_blob(GPG_ASCII)
        fingerprint = key.fingerprint.replace(" ", "").upper()

        binary_resp = await local_client.get(f"/pks/v2/vfpget/{fingerprint}")
        assert binary_resp.status_code == 200
        assert binary_resp.content == GPG_BINARY

        lookup_resp = await local_client.get(f"/pks/lookup?op=get&search={fingerprint}")
        assert lookup_resp.status_code == 200
        assert lookup_resp.text.strip() == GPG_ASCII.strip()


async def test_v2_vfpget_returns_requested_key_when_multiple_present(client):
    first_armored, _, first_fp = _make_key("one@example.com")
    second_armored, _, second_fp = _make_key("two@example.com")

    for payload in (first_armored, second_armored):
        resp = await client.post(
            "/pks/add",
            data={"keytext": payload},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert resp.status_code == 200

    first_resp = await client.get(f"/pks/v2/vfpget/{first_fp}")
    assert first_resp.status_code == 200
    first_key, _ = PGPKey.from_blob(first_resp.content)
    assert first_key.fingerprint.replace(" ", "").upper() == first_fp

    second_resp = await client.get(f"/pks/v2/vfpget/{second_fp}")
    assert second_resp.status_code == 200
    second_key, _ = PGPKey.from_blob(second_resp.content)
    assert second_key.fingerprint.replace(" ", "").upper() == second_fp
    assert first_resp.content != second_resp.content


async def test_v2_add_binary_submission_contract(client, sample_key):
    resp = await client.post(
        "/pks/v2/add",
        content=sample_key.binary,
        headers={"Content-Type": "application/pgp-keys; encoding=binary"},
    )
    assert resp.status_code in (200, 202)
    assert resp.headers.get("Access-Control-Allow-Origin") == "*"
    body = resp.json()
    assert "inserted" in body


async def test_post_fingerprint_merge_updates_flags(seeded_client, sample_key):
    revoked_at = dt.datetime.now(dt.timezone.utc).isoformat()
    payload = {
        "revoked": True,
        "revoked_at": revoked_at,
        "bits": 4096,
    }
    resp = await seeded_client.post(f"/pks/{sample_key.fingerprint}", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["revoked"] is True
    assert body["bits"] == 4096
    assert body["revoked_at"] == revoked_at


async def test_v2_authget_exact_match(seeded_client, sample_key):
    resp = await seeded_client.get(f"/pks/v2/authget/{sample_key.email}")
    assert resp.status_code == 200
    assert resp.headers.get("Access-Control-Allow-Origin") == "*"
    assert resp.content


async def test_v2_prefixlog_returns_prefixes(seeded_client):
    today = dt.date.today().isoformat()
    resp = await seeded_client.get(f"/pks/v2/prefixlog/{today}")
    assert resp.status_code == 200
    body = resp.text
    # Either empty or contains hex prefixes per line
    for line in body.splitlines():
        if not line.strip():
            continue
        int(line, 16)


async def test_v2_tokensend_returns_501(client):
    resp = await client.post(
        "/pks/v2/tokensend",
        content=b"user@example.com",
        headers={"Content-Type": "text/plain"},
    )
    assert resp.status_code == 501
    assert resp.headers.get("Access-Control-Allow-Origin") == "*"


async def test_v2_unknown_query_strings_are_ignored(seeded_client, sample_key):
    resp = await seeded_client.get(
        f"/pks/v2/index/{sample_key.email}?x-ignore=1&y-ignore=2"
    )
    assert resp.status_code == 200


async def test_republishing_key_does_not_duplicate_uids(seeded_client, sample_key):
    for _ in range(3):
        resp = await seeded_client.post(
            "/pks/v2/add",
            content=sample_key.binary,
            headers={"Content-Type": "application/pgp-keys; encoding=binary"},
        )
        assert resp.status_code in (200, 202)

    resp = await seeded_client.get(f"/pks/v2/index/{sample_key.fingerprint}")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload and len(payload[0]["uids"]) == 1
    assert payload[0]["uids"][0].endswith("<user@example.com>")


async def test_republishing_revoked_key_updates_status(client, sample_key):
    resp = await client.post(
        "/pks/v2/add",
        content=sample_key.binary,
        headers={"Content-Type": "application/pgp-keys; encoding=binary"},
    )
    assert resp.status_code in (200, 202)

    key, _ = PGPKey.from_blob(sample_key.armored)
    pubkey = key.pubkey
    with key.unlock(None):
        revoke_sig = key.revoke(pubkey, reason=RevocationReason.Retired)
    pubkey |= revoke_sig

    resp = await client.post(
        "/pks/v2/add",
        content=bytes(pubkey),
        headers={"Content-Type": "application/pgp-keys; encoding=binary"},
    )
    assert resp.status_code in (200, 202)

    resp = await client.get(f"/pks/v2/index/{sample_key.fingerprint}")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload and payload[0]["revoked"] is True
    assert payload[0]["revoked_at"] is not None


async def test_stale_material_does_not_restore_revocation(client, sample_key):
    resp = await client.post(
        "/pks/v2/add",
        content=sample_key.binary,
        headers={"Content-Type": "application/pgp-keys; encoding=binary"},
    )
    assert resp.status_code in (200, 202)

    key, _ = PGPKey.from_blob(sample_key.armored)
    pubkey = key.pubkey
    with key.unlock(None):
        revoke_sig = key.revoke(pubkey, reason=RevocationReason.Retired)
    pubkey |= revoke_sig

    resp = await client.post(
        "/pks/v2/add",
        content=bytes(pubkey),
        headers={"Content-Type": "application/pgp-keys; encoding=binary"},
    )
    assert resp.status_code in (200, 202)

    resp = await client.get(f"/pks/v2/index/{sample_key.fingerprint}")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload and payload[0]["revoked"] is True
    revoked_at = payload[0]["revoked_at"]
    assert revoked_at is not None

    resp = await client.post(
        "/pks/v2/add",
        content=sample_key.binary,
        headers={"Content-Type": "application/pgp-keys; encoding=binary"},
    )
    assert resp.status_code in (200, 202)

    resp = await client.get(f"/pks/v2/index/{sample_key.fingerprint}")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload and payload[0]["revoked"] is True
    assert payload[0]["revoked_at"] == revoked_at
