"""Execute the README example with `python README_example.py`."""

import asyncio

import httpx

from swarmauri_tokens_introspection import IntrospectionTokenService


async def main() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url == httpx.URL("https://auth.example.com/introspect")
        assert request.headers["Authorization"].startswith("Basic ")
        form = dict(httpx.QueryParams(request.content.decode()))
        assert form["token"] == "opaque-token"
        return httpx.Response(
            200,
            json={
                "active": True,
                "sub": "user-123",
                "scope": "profile email",
                "exp": 2_147_483_647,
            },
        )

    transport = httpx.MockTransport(handler)

    service = IntrospectionTokenService(
        "https://auth.example.com/introspect",
        client_id="id",
        client_secret="secret",
        cache_ttl_s=300,
    )

    # Inject the mock transport; in production you would not override the client.
    service._client = httpx.AsyncClient(transport=transport)

    claims = await service.verify("opaque-token")
    print(claims["sub"])  # user-123

    await service.aclose()


if __name__ == "__main__":
    asyncio.run(main())
