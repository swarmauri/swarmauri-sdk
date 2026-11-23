from swarmauri_canon_http import HttpClient

client = HttpClient(base_url="https://example.com", timeout=5)
status, headers, body = client.get("/health", params={"full": "1"})
print(status, body)
