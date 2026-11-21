from swarmauri_storage_minio import MinioStorageAdapter
import io

adapter = MinioStorageAdapter(
    endpoint="localhost:9000",
    access_key="minio",
    secret_key="minio123",
    bucket="peagen",
    secure=False,
    prefix="examples/",
)
uri = adapter.upload("artifact.txt", io.BytesIO(b"data"))
print(uri)

downloaded = adapter.download("artifact.txt").read()
print(downloaded.decode("utf-8"))
