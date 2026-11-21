import base64
import hashlib
import hmac
import json

from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from swarmauri_middleware_httpsig import HttpSigMiddleware


app = Starlette()
http_sig = HttpSigMiddleware(secret_key="supersecret")


async def verify_signature(request: Request, call_next):
    try:
        return await http_sig.dispatch(request, call_next)
    except HTTPException as exc:
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.detail}
        )


app.add_middleware(BaseHTTPMiddleware, dispatch=verify_signature)


async def echo(request: Request):
    return JSONResponse(await request.json())


app.add_route("/echo", echo, methods=["POST"])


def create_signature(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode(), body, hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


if __name__ == "__main__":
    client = TestClient(app)

    body = json.dumps({"message": "hello"}).encode()
    signature = create_signature("supersecret", body)

    ok = client.post(
        "/echo",
        data=body,
        headers={
            "X-Signature": signature,
            "Content-Type": "application/json",
        },
    )
    assert ok.status_code == 200
    print("Verified response:", ok.json())

    bad = client.post(
        "/echo",
        data=body,
        headers={
            "X-Signature": "tampered",
            "Content-Type": "application/json",
        },
    )
    assert bad.status_code == 401
    print("Unauthorized status:", bad.status_code)
