import inspect
from fastapi import FastAPI, HTTPException
from pydantic import create_model
import uvicorn
import nest_asyncio

# Create a FastAPI instance.
app = FastAPI()

def register_tool_instance(app: FastAPI, instance) -> None:
    """
    Registers an instance's __call__ method as a FastAPI POST route.
    Automatically generates a Pydantic request model from the __call__ method's signature
    and derives a route from the instance's class name.

    Args:
        app (FastAPI): The FastAPI application instance.
        instance: The instance whose __call__ method will be exposed.
    """
    func = instance.__call__
    sig = inspect.signature(func)
    fields = {}
    for name, param in sig.parameters.items():
        # Skip 'self' if present.
        if name == "self":
            continue
        annotation = param.annotation if param.annotation is not param.empty else str
        default = param.default if param.default is not param.empty else ...
        fields[name] = (annotation, default)
    
    # Dynamically create a Pydantic model for request validation.
    RequestModel = create_model(f"{instance.__class__.__name__}Request", **fields)
    
    async def endpoint(request: RequestModel):
        try:
            # Call the __call__ method using the validated data.
            result = func(**request.model_dump())
            return result
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    # Derive the route from the class name (converted to lowercase).
    route_path = f"/{instance.__class__.__name__.lower()}"
    app.post(route_path)(endpoint)

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
            "metrics": {metric: 0.0 for metric in metrics}
        }
        return {"metrics_data": metrics_data}

# Create an instance of MetricsTool.
metrics_tool = MetricsTool()

# Programmatically register the instance's __call__ method.
register_tool_instance(app, metrics_tool)

# --- Launching the FastAPI server in a Jupyter Notebook ---
# Patch the event loop for Jupyter Notebook compatibility.
nest_asyncio.apply()

# Run the server using uvicorn (non-blocking in Jupyter Notebook).
uvicorn.run(app, host="localhost", port=8020)
