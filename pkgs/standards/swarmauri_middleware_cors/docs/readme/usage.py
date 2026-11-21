from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from swarmauri_middleware_cors import CustomCORSMiddleware

app = Starlette()

cors = CustomCORSMiddleware(
    allow_origins=["https://frontend.example"],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["Authorization"],
    expose_headers=["X-App-Version"],
    max_age=300,
)


async def apply_custom_cors(request, call_next):
    return await cors.dispatch(request, call_next)


app.add_middleware(BaseHTTPMiddleware, dispatch=apply_custom_cors)


async def ping(_request):
    return JSONResponse({"status": "ok"})


app.add_route("/ping", ping)

client = TestClient(app)

if __name__ == "__main__":
    options_response = client.options(
        "/ping", headers={"Origin": "https://frontend.example"}
    )
    print(
        "Allowed origin header:",
        options_response.headers["Access-Control-Allow-Origin"],
    )

    response = client.get(
        "/ping", headers={"Origin": "https://frontend.example"}
    )
    print("Response JSON:", response.json())
