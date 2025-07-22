# AutoAPI Client

A tiny, dependency-free HTTP client for AutoAPI with support for all HTTP methods and both synchronous and asynchronous operations.

## Features

- **Full HTTP Support**: GET, POST, PUT, PATCH, DELETE methods
- **Async & Sync**: Both synchronous and asynchronous variants of all methods
- **Schema Validation**: Optional Pydantic schema validation for request/response data
- **JSON-RPC Compatible**: Backward compatible with existing JSON-RPC calls
- **Context Managers**: Support for both sync and async context managers
- **Custom Headers**: Support for custom HTTP headers
- **Error Handling**: Proper HTTP and JSON-RPC error handling

## Installation

```bash
pip install httpx  # Required dependency
pip install pydantic  # Optional, for schema validation
```

## Quick Start

### Synchronous Usage

```python
from autoapi_client import AutoAPIClient

# Create client
client = AutoAPIClient("https://api.example.com")

# GET request
user = client.get("/users/1")

# POST request with data
new_user = client.post("/users", params={
    "name": "John Doe",
    "email": "john@example.com"
})

# PUT request
updated_user = client.put("/users/1", params={
    "name": "Jane Doe",
    "email": "jane@example.com"
})

# PATCH request (partial update)
patched_user = client.patch("/users/1", params={"name": "New Name"})

# DELETE request
client.delete("/users/1")

# Custom headers
response = client.get("/protected", headers={
    "Authorization": "Bearer your-token"
})

client.close()
```

### Asynchronous Usage

```python
import asyncio
from autoapi_client import AutoAPIClient

async def main():
    client = AutoAPIClient("https://api.example.com")

    # Async GET request
    user = await client.aget("/users/1")

    # Async POST request
    new_user = await client.apost("/users", params={
        "name": "John Doe",
        "email": "john@example.com"
    })

    # Async PUT request
    updated_user = await client.aput("/users/1", params={
        "name": "Jane Doe"
    })

    # Async PATCH request
    patched_user = await client.apatch("/users/1", params={
        "email": "newemail@example.com"
    })

    # Async DELETE request
    await client.adelete("/users/1")

    await client.aclose()

asyncio.run(main())
```

### Context Managers

```python
# Synchronous context manager
with AutoAPIClient("https://api.example.com") as client:
    user = client.get("/users/1")

# Asynchronous context manager
async def example():
    async with AutoAPIClient("https://api.example.com") as client:
        user = await client.aget("/users/1")
```

### Schema Validation with Pydantic

```python
from pydantic import BaseModel
from autoapi_client import AutoAPIClient

class User(BaseModel):
    id: int
    name: str
    email: str

class CreateUser(BaseModel):
    name: str
    email: str

client = AutoAPIClient("https://api.example.com")

# Request with schema validation
user_data = CreateUser(name="John", email="john@example.com")
response = client.post("/users", params=user_data, out_schema=User)

# Response is automatically validated and converted to User instance
print(response.name)  # Type-safe access
```

### JSON-RPC Backward Compatibility

The original `call` method is still supported for JSON-RPC endpoints:

```python
client = AutoAPIClient("https://jsonrpc.example.com/api")

# Legacy JSON-RPC call
result = client.call("getUserById", params={"id": 123})
```

## API Reference

### Constructor

```python
AutoAPIClient(
    endpoint: str,
    *,
    client: httpx.Client | None = None,
    async_client: httpx.AsyncClient | None = None
)
```

### Synchronous Methods

- `get(url=None, *, params=None, headers=None, out_schema=None)`
- `post(url=None, *, params=None, headers=None, out_schema=None)`
- `put(url=None, *, params=None, headers=None, out_schema=None)`
- `patch(url=None, *, params=None, headers=None, out_schema=None)`
- `delete(url=None, *, params=None, headers=None, out_schema=None)`

### Asynchronous Methods

- `aget(url=None, *, params=None, headers=None, out_schema=None)`
- `apost(url=None, *, params=None, headers=None, out_schema=None)`
- `aput(url=None, *, params=None, headers=None, out_schema=None)`
- `apatch(url=None, *, params=None, headers=None, out_schema=None)`
- `adelete(url=None, *, params=None, headers=None, out_schema=None)`

### Legacy Method

- `call(method, *, params=None, out_schema=None)` - JSON-RPC compatibility

### Parameters

- `url`: Optional URL path (uses base endpoint if None)
- `params`: Request data (dict or Pydantic model)
- `headers`: Custom HTTP headers (dict)
- `out_schema`: Optional Pydantic model class for response validation

## Error Handling

The client handles both HTTP errors and JSON-RPC errors:

```python
try:
    response = client.get("/nonexistent")
except httpx.HTTPStatusError as e:
    print(f"HTTP error: {e}")
except RuntimeError as e:
    print(f"JSON-RPC error: {e}")
```

## Examples

See `example_usage.py` for comprehensive usage examples demonstrating all features.

## Requirements

- Python 3.7+
- httpx
- pydantic (optional, for schema validation)
