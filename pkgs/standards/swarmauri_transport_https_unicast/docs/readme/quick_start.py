import asyncio

from swarmauri_transport_https_unicast import (
    HttpsSecurityPolicy,
    HttpsUnicastTransport,
)


async def main() -> None:
    body = b'{"order_id":"ord_1001"}'
    jws_key = {
        "kind": "raw",
        "key": b"transport-demo-secret-32-bytes!!",
        "kid": "body.1",
    }
    policy = HttpsSecurityPolicy(
        bearer_token="jwt-or-other-bearer-token",
        http_signature_secret="shared-secret",
        request_jws_key=jws_key,
        request_jws_kid="body.1",
        response_jws_key=jws_key,
    )
    transport = HttpsUnicastTransport(
        base_url="https://127.0.0.1:8443",
        verify="/path/to/trust-anchor.pem",
        security_policy=policy,
        require_response_jws=True,
    )

    async with transport.client():
        status, headers, response_body = await transport.request(
            "POST", "/secure/orders", body=body
        )

    print(status, headers["content-type"], response_body)
    print(transport.last_evidence)


asyncio.run(main())
