import inspect
import json
from typing import Any

from pydantic import TypeAdapter, ValidationError, create_model
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
import uvicorn
import nest_asyncio

app = Starlette()
_tool_result_adapter = TypeAdapter(Any)


def register_tool_instance(app: Starlette, instance) -> None:
    """
    Registers an instance's __call__ method as a Starlette POST route.
    Build a Pydantic request model from the __call__ method's signature and
    derive the route from the instance's class name.

    Args:
        app: The Starlette application instance.
        instance: The instance whose __call__ method will be exposed.
    """
    func = instance.__call__
    sig = inspect.signature(func)
    fields = {}
    for name, param in sig.parameters.items():
        # Skip 'self' if present.
        if name == "self":
            continue
        annotation = (
            param.annotation if param.annotation is not param.empty else str
        )
        default = param.default if param.default is not param.empty else ...
        fields[name] = (annotation, default)

    # Dynamically create a Pydantic model for request validation.
    RequestModel = create_model(
        f"{instance.__class__.__name__}Request", **fields
    )

    async def endpoint(request: Request) -> JSONResponse:
        try:
            payload = RequestModel.model_validate(await request.json())
        except ValidationError as exc:
            errors = json.loads(
                exc.json(include_context=False, include_url=False)
            )
            for error in errors:
                error["loc"].insert(0, "body")
            return JSONResponse({"detail": errors}, status_code=422)
        except ValueError as exc:
            return JSONResponse({"detail": str(exc)}, status_code=422)

        try:
            # Call the __call__ method using the validated data.
            result = func(**payload.model_dump(mode="python"))
            content = _tool_result_adapter.dump_python(
                result, mode="json", by_alias=True
            )
            return JSONResponse(content)
        except Exception as exc:
            return JSONResponse({"detail": str(exc)}, status_code=400)

    # Derive the route from the class name (converted to lowercase).
    route_path = f"/{instance.__class__.__name__.lower()}"
    app.router.routes.append(Route(route_path, endpoint, methods=["POST"]))


# Define a tool class with a __call__ method.
class MetricsTool:
    def __call__(self, metrics: list[str], sampling_interval: float) -> dict:
        """
        Simulates collecting system metrics.

        Args:
            metrics (list[str]): List of metric names to collect.
            sampling_interval (float): Time in seconds between measurements.

        Returns:
            dict: A dictionary containing simulated metrics data.
        """
        metrics_data = {
            "timestamp": "2025-02-19T12:00:00",
            "metrics": {metric: 0.0 for metric in metrics},
        }
        return {"metrics_data": metrics_data}


# Create an instance of MetricsTool.
metrics_tool = MetricsTool()

# Programmatically register the instance's __call__ method.
register_tool_instance(app, metrics_tool)

if __name__ == "__main__":
    # Patch the event loop for Jupyter Notebook compatibility.
    nest_asyncio.apply()
    uvicorn.run(app, host="localhost", port=8020)
