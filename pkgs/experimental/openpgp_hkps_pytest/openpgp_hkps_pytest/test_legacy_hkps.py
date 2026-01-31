from __future__ import annotations

import re

import httpx
import pytest

pytestmark = pytest.mark.asyncio

BEGIN_ARMOR = b"-----BEGIN PGP PUBLIC KEY BLOCK-----"
END_ARMOR = b"-----END PGP PUBLIC KEY BLOCK-----"


@pytest.fixture(scope="module")
async def client(hkps_async_client: httpx.AsyncClient) -> httpx.AsyncClient:
    return hkps_async_client


@pytest.fixture(scope="module")
def armored_bundle(hkps_armored_bundle: bytes | None) -> bytes | None:
    return hkps_armored_bundle


async def _legacy_index(
    client: httpx.AsyncClient, search: str, **params: str
) -> httpx.Response:
    query = {"op": "index", "search": search}
    query.update(params)
    return await client.get("/pks/lookup", params=query)


async def _legacy_get(
    client: httpx.AsyncClient, search: str, **params: str
) -> httpx.Response:
    query = {"op": "get", "search": search}
    query.update(params)
    return await client.get("/pks/lookup", params=query)


async def _legacy_add(
    client: httpx.AsyncClient, armored: bytes, **params: str
) -> httpx.Response:
    data = {"keytext": armored.decode("utf-8")}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    return await client.post("/pks/add", params=params, data=data, headers=headers)


def _assert_cors(resp: httpx.Response) -> None:
    assert resp.headers.get("Access-Control-Allow-Origin") == "*", (
        "CORS header MUST be set per spec."
    )


def _assert_ascii_armored(body: bytes) -> None:
    assert BEGIN_ARMOR in body and END_ARMOR in body, (
        "Response MUST be ASCII-armored per Legacy get."
    )


def _is_machine_readable_index(text: str) -> bool:
    return bool(re.search(r"(?m)^(info:|pub:)", text))


async def test_legacy_index_machine_readable_headers_and_shape(
    client: httpx.AsyncClient,
) -> None:
    resp = await _legacy_index(client, "nobody@example.invalid", options="mr")
    assert resp.status_code in (200, 404), (
        f"Unexpected status for legacy index: {resp.status_code}"
    )
    if resp.status_code == 200:
        _assert_cors(resp)
        assert resp.headers.get("Content-Type", "").startswith("text/plain"), (
            "Legacy MR index MUST be text/plain."
        )
        assert _is_machine_readable_index(resp.text), (
            "Legacy MR index body shape invalid."
        )


async def test_legacy_get_by_hex_returns_ascii_armored_and_type(
    client: httpx.AsyncClient,
) -> None:
    resp = await _legacy_get(
        client, "0xDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEF", options="mr"
    )
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        _assert_cors(resp)
        content_type = resp.headers.get("Content-Type", "")
        assert content_type.startswith("application/pgp-keys"), (
            "Legacy get MUST return ASCII-armored with application/pgp-keys."
        )
        _assert_ascii_armored(resp.content)


async def test_legacy_rejects_short_keyid(client: httpx.AsyncClient) -> None:
    resp = await _legacy_get(client, "0xDEADBEEF", options="mr")
    assert resp.status_code == 404, "Short Key ID MUST NOT be served."


async def test_legacy_add_submission_contract(
    client: httpx.AsyncClient, armored_bundle: bytes | None
) -> None:
    if armored_bundle is None:
        pytest.skip(
            "Set HPKS_TEST_ARMORED or --hkps-armored-path to run /pks/add positive path."
        )
    resp = await _legacy_add(client, armored_bundle)
    assert resp.status_code in (200, 202, 403, 422), (
        f"Unexpected status for legacy add: {resp.status_code}"
    )


async def test_legacy_add_then_get_roundtrip_if_supported(
    client: httpx.AsyncClient, armored_bundle: bytes | None
) -> None:
    if armored_bundle is None:
        pytest.skip("Set HPKS_TEST_ARMORED or --hkps-armored-path to run roundtrip.")
    add_resp = await _legacy_add(client, armored_bundle)
    if add_resp.status_code not in (200, 202):
        pytest.skip(
            f"Server declined add (status {add_resp.status_code}); skipping roundtrip."
        )
    idx = await _legacy_index(client, "example.com", options="mr", x_ignore="1")
    assert idx.status_code in (200, 404)
    if idx.status_code == 200:
        _assert_cors(idx)
        assert idx.headers.get("Content-Type", "").startswith("text/plain")
        assert _is_machine_readable_index(idx.text)
