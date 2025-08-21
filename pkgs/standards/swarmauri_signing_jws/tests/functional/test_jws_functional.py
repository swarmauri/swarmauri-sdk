import asyncio
import base64
import json

from swarmauri_signing_jws import JwsSignerVerifier


async def _run() -> bool:
    jws = JwsSignerVerifier()
    key1 = {"kind": "raw", "key": "one"}
    key2 = {"kind": "raw", "key": "two"}
    payload = {"msg": "func"}
    general = await jws.sign_general_json(
        payload=payload,
        signatures=[
            ("HS256", key1, None, None),
            ("HS512", key2, None, None),
        ],
    )
    accepted, out_payload = await jws.verify_general_json(
        general,
        hmac_keys=[key1, key2],
        require_any=["HS256", "HS512"],
        min_signers=2,
    )
    tampered = dict(general)
    bad_payload = (
        base64.urlsafe_b64encode(
            json.dumps({"msg": "bad"}, separators=(",", ":")).encode()
        )
        .rstrip(b"=")
        .decode()
    )
    tampered["payload"] = bad_payload
    bad_accepted, _ = await jws.verify_general_json(
        tampered,
        hmac_keys=[key1, key2],
        require_any=["HS256", "HS512"],
        min_signers=2,
    )
    return accepted == 2 and out_payload == b'{"msg":"func"}' and bad_accepted == 0


def test_jws_general_functional() -> None:
    assert asyncio.run(_run())
