from swarmauri_storage_s3fs import S3FSStorageAdapter

adapter = S3FSStorageAdapter.from_uri("s3://model-artifacts/runs")
uri = adapter.put_blob("latest/result.json", b'{"status":"ok"}')
payload = adapter.get_blob("latest/result.json")

print(uri)
print(payload)
