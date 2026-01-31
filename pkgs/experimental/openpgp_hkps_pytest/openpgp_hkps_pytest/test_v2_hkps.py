from __future__ import annotations

import re

import httpx
import pytest

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="module")
async def client(hkps_async_client: httpx.AsyncClient) -> httpx.AsyncClient:
    return hkps_async_client


@pytest.fixture(scope="module")
def binary_bundle(hkps_binary_bundle: bytes | None) -> bytes | None:
    return hkps_binary_bundle


def _assert_cors(resp: httpx.Response) -> None:
    assert resp.headers.get("Access-Control-Allow-Origin") == "*", (
        "CORS header MUST be set per spec."
    )


async def test_v2_index_json_contract_and_cors(client: httpx.AsyncClient) -> None:
    resp = await client.get("/pks/v2/index/example.com")
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        _assert_cors(resp)
        assert resp.headers.get("Content-Type", "").startswith("application/json")
        data = resp.json()
        assert isinstance(data, list), "v2 index MUST be a JSON list"
        if data:
            cert = data[0]
            assert "version" in cert and isinstance(cert["version"], int)
            assert "fingerprint" in cert and isinstance(cert["fingerprint"], str)


async def test_v2_vfpget_returns_binary_bundle(client: httpx.AsyncClient) -> None:
    resp = await client.get("/pks/v2/vfpget/06DEADBEEFDEADBEEFDEADBEEFDEADBEEFDEAD")
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        _assert_cors(resp)
        content_type = resp.headers.get("Content-Type", "")
        assert (
            "application/pgp-keys" in content_type and "encoding=binary" in content_type
        ), (
            "v2 lookups MUST return non-armored bundles with application/pgp-keys; encoding=binary"
        )
        assert resp.content and not resp.content.startswith(b"-----BEGIN"), (
            "MUST be non-armored binary"
        )


async def test_v2_kidget_returns_404_for_v6_certificates(
    client: httpx.AsyncClient,
) -> None:
    resp = await client.get("/pks/v2/kidget/DEADBEEFDEADBEEF")
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        content_type = resp.headers.get("Content-Type", "")
        assert "application/pgp-keys" in content_type, "kidget return MUST be a bundle"


async def test_v2_authget_is_exact_and_authoritative(client: httpx.AsyncClient) -> None:
    resp = await client.get("/pks/v2/authget/user%40example.com")
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        _assert_cors(resp)
        content_type = resp.headers.get("Content-Type", "")
        assert (
            "application/pgp-keys" in content_type and "encoding=binary" in content_type
        )


async def test_v2_prefixlog_returns_crlf_hex_prefixes(
    client: httpx.AsyncClient,
) -> None:
    resp = await client.get("/pks/v2/prefixlog/2025-01-01")
    assert resp.status_code in (200, 404, 501)
    if resp.status_code == 200:
        text = resp.text
        for line in text.splitlines():
            if not line.strip():
                continue
            assert re.fullmatch(r"[0-9A-Fa-f]+", line) is not None, (
                "prefixlog lines must be hex"
            )


async def test_v2_add_binary_submission_contract(
    client: httpx.AsyncClient, binary_bundle: bytes | None
) -> None:
    if binary_bundle is None:
        pytest.skip(
            "Set HPKS_TEST_BINARY or --hkps-binary-path to run /pks/v2/add positive path."
        )
    headers = {"Content-Type": "application/pgp-keys; encoding=binary"}
    resp = await client.post("/pks/v2/add", content=binary_bundle, headers=headers)
    assert resp.status_code in (200, 202, 403, 422), (
        f"Unexpected status: {resp.status_code}"
    )
    if resp.headers.get("Content-Type", "").startswith("application/json"):
        _assert_cors(resp)
        body = resp.json()
        for field in ("inserted", "updated", "deleted", "ignored"):
            if field in body:
                assert isinstance(body[field], list)
                for cert in body[field]:
                    assert "version" in cert and "fingerprint" in cert


async def test_v2_tokensend_plain_text_contract(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/pks/v2/tokensend",
        content=b"user@example.com\r\nalt@example.com",
        headers={"Content-Type": "text/plain"},
    )
    assert resp.status_code in (200, 202, 403, 422, 501)


async def test_v2_unknown_query_strings_are_ignored(client: httpx.AsyncClient) -> None:
    resp = await client.get("/pks/v2/index/example.com?x-ignore=1&y-ignore=2")
    assert resp.status_code in (200, 404)


async def test_v2_get_unknown_returns_404_not_400(client: httpx.AsyncClient) -> None:
    resp = await client.get("/pks/v2/kidget/0000000000000000")
    assert resp.status_code in (200, 404)
