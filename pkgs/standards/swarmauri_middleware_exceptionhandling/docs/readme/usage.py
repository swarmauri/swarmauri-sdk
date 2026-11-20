from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.testclient import TestClient

from swarmauri_middleware_exceptionhandling import ExceptionHandlingMiddleware

app = Starlette()
app.add_middleware(BaseHTTPMiddleware, dispatch=ExceptionHandlingMiddleware())


async def boom(_request):
    raise RuntimeError("Boom!")


app.add_route("/boom", boom)

client = TestClient(app)
response = client.get("/boom")
assert response.status_code == 500
print(response.json())
