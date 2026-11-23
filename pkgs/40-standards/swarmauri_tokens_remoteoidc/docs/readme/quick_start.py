import asyncio
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import jwt
from jwt.utils import base64url_encode

from swarmauri_tokens_remoteoidc import RemoteOIDCTokenService

SECRET = b"super-secret-key"
KEY_ID = "demo-key"


def make_handler(jwks: dict):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != "/jwks.json":
                self.send_response(404)
                self.end_headers()
                return

            body = json.dumps(jwks).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(
            self, format, *args
        ):  # pragma: no cover - quiet server
            return

    return Handler


async def main() -> None:
    jwks = {
        "keys": [
            {
                "kty": "oct",
                "kid": KEY_ID,
                "k": base64url_encode(SECRET).decode("ascii"),
                "alg": "HS256",
            }
        ]
    }

    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(jwks))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        issuer = "https://issuer.example.com"
        jwks_url = f"http://127.0.0.1:{server.server_address[1]}/jwks.json"

        service = RemoteOIDCTokenService(
            issuer=issuer,
            jwks_url=jwks_url,
            expected_alg_whitelist=("HS256",),
        )

        now = int(time.time())
        token = jwt.encode(
            {
                "iss": issuer,
                "aud": "my-audience",
                "sub": "user-123",
                "iat": now,
                "exp": now + 60,
            },
            SECRET,
            algorithm="HS256",
            headers={"kid": KEY_ID},
        )

        service.refresh(force=True)
        claims = await service.verify(token, audience="my-audience")
        print(f"Verified subject: {claims['sub']}")
    finally:
        server.shutdown()
        thread.join()


if __name__ == "__main__":
    asyncio.run(main())
