import datetime as dt

import pytest
from pgpy import PGPKey
from pgpy.constants import RevocationReason

pytestmark = pytest.mark.asyncio


async def test_v2_index_json_contract_and_cors(seeded_client, sample_key):
    resp = await seeded_client.get(f"/pks/v2/index/{sample_key.email}")
    assert resp.status_code == 200
    assert resp.headers.get("Access-Control-Allow-Origin") == "*"
    data = resp.json()
    assert isinstance(data, list)
    assert data and data[0]["fingerprint"] == sample_key.fingerprint


async def test_v2_vfpget_returns_binary_bundle(seeded_client, sample_key):
    resp = await seeded_client.get(f"/pks/v2/vfpget/{sample_key.fingerprint}")
    assert resp.status_code == 200
    assert resp.headers.get("Access-Control-Allow-Origin") == "*"
    ctype = resp.headers.get("Content-Type", "")
    assert "application/pgp-keys" in ctype and "encoding=binary" in ctype
    assert resp.content.startswith(b"-----") is False


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
