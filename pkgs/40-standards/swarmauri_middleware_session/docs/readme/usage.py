from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from swarmauri_middleware_session import SessionMiddleware


app = Starlette()
session_middleware = SessionMiddleware()


async def attach_session(request: Request, call_next):
    return await session_middleware.dispatch(request, call_next)


app.add_middleware(BaseHTTPMiddleware, dispatch=attach_session)


async def greet(request: Request):
    session_id = request.state.session_id
    session_data = session_middleware.session_storage.setdefault(
        session_id, {}
    )
    session_data["visits"] = session_data.get("visits", 0) + 1
    return JSONResponse(
        {"session_id": session_id, "visits": session_data["visits"]}
    )


app.add_route("/greet", greet)

client = TestClient(app)

first_response = client.get("/greet")
first_data = first_response.json()

second_response = client.get(
    "/greet", headers={"X-Session-ID": first_response.headers["X-Session-ID"]}
)
second_data = second_response.json()

print(first_data)
print(second_data)
