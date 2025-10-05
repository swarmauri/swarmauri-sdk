from __future__ import annotations

async def validate_http01(ctx, domain: str, token: str, key_authorization: str) -> bool:
    http = ctx.get("http_client")
    if http is None:
        # Expect runtime to inject an async http client with .get(url) -> (status, text)
        raise RuntimeError("http_client not available in ctx")
    url = f"http://{domain}/.well-known/acme-challenge/{token}"
    status, body = await http.get(url)
    if status != 200:
        return False
    return (body or "").strip() == key_authorization
