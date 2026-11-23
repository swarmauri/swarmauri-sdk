from swarmauri_storage_s3_over_sftp import S3OverSftpStorageAdapter

adapter = S3OverSftpStorageAdapter.from_uri(
    "s3+sftp://deploy@example.com/artifacts/runs?root_dir=/srv/object-store"
)

uri = adapter.put_blob("latest/result.json", b'{"status":"ok"}')
payload = adapter.get_blob("latest/result.json")

print(uri)
print(payload)
