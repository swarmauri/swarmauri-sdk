

from swarmauri_gitfilter_minio import MinioFilter


class DummyClient:
    def __init__(self, *a, **k):
        pass

    def bucket_exists(self, bucket):
        return True

    def make_bucket(self, bucket):
        pass

    def get_object(self, bucket, key):
        class Resp:
            def read(self):
                return b""

            def close(self):
                pass

            def release_conn(self):
                pass

        return Resp()

    def put_object(self, *a, **k):
        pass

    def list_objects(self, *a, **k):
        return []


def test_from_uri(monkeypatch):
    monkeypatch.setattr(
        "swarmauri_gitfilter_minio.minio_filter.Minio",
        DummyClient,
    )
    filt = MinioFilter.from_uri("minio://example.com/bucket")
    assert isinstance(filt, MinioFilter)
