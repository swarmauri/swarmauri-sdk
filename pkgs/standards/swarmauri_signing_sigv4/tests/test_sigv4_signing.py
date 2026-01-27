from typing import Mapping

import pytest

from swarmauri_signing_sigv4 import SigV4Signing


@pytest.fixture()
def sigv4_envelope() -> Mapping[str, object]:
    return {
        "method": "GET",
        "uri": "/",
        "query": {"Action": ["ListUsers"], "Version": ["2010-05-08"]},
        "headers": {
            "host": "iam.amazonaws.com",
            "x-amz-date": "20150830T123600Z",
            "content-type": "application/x-www-form-urlencoded; charset=utf-8",
        },
        "payload_hash": "UNSIGNED-PAYLOAD",
        "amz_date": "20150830T123600Z",
        "scope": {"date": "20150830", "region": "us-east-1", "service": "iam"},
    }


@pytest.fixture()
def sigv4_key() -> Mapping[str, str]:
    return {
        "access_key": "AKIDEXAMPLE",
        "secret_key": "wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY",
    }


@pytest.mark.asyncio
async def test_canonical_request_matches_reference(sigv4_envelope):
    signer = SigV4Signing()
    canonical = (await signer.canonicalize_envelope(sigv4_envelope)).decode()
    assert canonical == (
        "GET\n"
        "/\n"
        "Action=ListUsers&Version=2010-05-08\n"
        "content-type:application/x-www-form-urlencoded; charset=utf-8\n"
        "host:iam.amazonaws.com\n"
        "x-amz-date:20150830T123600Z\n\n"
        "content-type;host;x-amz-date\n"
        "UNSIGNED-PAYLOAD"
    )


@pytest.mark.asyncio
async def test_sign_envelope_produces_expected_signature(sigv4_key, sigv4_envelope):
    signer = SigV4Signing()
    signatures = await signer.sign_envelope(sigv4_key, sigv4_envelope)
    signature = signatures[0]
    assert (
        signature["signature"]
        == "86116edbb7e0e8c675dc9cfa9fcfcd0115a98ee9cc1196e4623cd2673a806766"
    )
    assert signature["scope"] == "20150830/us-east-1/iam/aws4_request"
    assert signature["signed_headers"] == "content-type;host;x-amz-date"
    assert (
        signature["canonical_request_sha256"]
        == "2714b15fec5795e21b0fa0c48f6944f639224b42fd8e71d16f57ed58265f9c7d"
    )


@pytest.mark.asyncio
async def test_verify_envelope_with_secret(sigv4_key, sigv4_envelope):
    signer = SigV4Signing()
    signatures = await signer.sign_envelope(sigv4_key, sigv4_envelope)
    assert await signer.verify_envelope(
        sigv4_envelope,
        signatures,
        opts={"secret_key": sigv4_key["secret_key"]},
    )


@pytest.mark.asyncio
async def test_sign_and_verify_bytes(sigv4_key):
    signer = SigV4Signing()
    payload = b"example-payload"
    opts = {"date": "20150830", "region": "us-east-1", "service": "iam"}
    signatures = await signer.sign_bytes(sigv4_key, payload, opts=opts)
    assert await signer.verify_bytes(
        payload,
        signatures,
        opts={**opts, "secret_key": sigv4_key["secret_key"]},
    )


@pytest.mark.asyncio
async def test_verify_envelope_without_secret_fails(sigv4_key, sigv4_envelope):
    signer = SigV4Signing()
    signatures = await signer.sign_envelope(sigv4_key, sigv4_envelope)
    assert not await signer.verify_envelope(sigv4_envelope, signatures)
