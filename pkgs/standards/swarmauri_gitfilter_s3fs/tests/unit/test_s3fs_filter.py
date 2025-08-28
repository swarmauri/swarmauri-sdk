import io


from swarmauri_gitfilter_s3fs import S3FSFilter


class DummyFS:
    def open(self, *args, **kwargs):
        return io.BytesIO()

    def find(self, base):
        return []


def test_from_uri(monkeypatch):
    monkeypatch.setattr(
        "swarmauri_gitfilter_s3fs.s3fs_filter.s3fs.S3FileSystem",
        lambda *a, **k: DummyFS(),
    )
    filt = S3FSFilter.from_uri("s3://bucket")
    assert isinstance(filt, S3FSFilter)
