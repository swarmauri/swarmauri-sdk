from swarmauri_transport_httpx import HttpxClient

with HttpxClient(base_url="https://api.example.com") as client:
    response = client.request("GET", "/models")
    response.raise_for_status()
