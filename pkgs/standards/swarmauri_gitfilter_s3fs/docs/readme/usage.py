from contextlib import nullcontext
from io import BytesIO
from unittest.mock import MagicMock, patch

from swarmauri_gitfilter_s3fs import S3FSFilter

with patch("swarmauri_gitfilter_s3fs.s3fs_filter.s3fs.S3FileSystem") as fs_cls:
    fake_fs = MagicMock()
    buffer = BytesIO()
    fake_fs.open.return_value = nullcontext(buffer)
    fs_cls.return_value = fake_fs

    filt = S3FSFilter.from_uri("s3://demo-bucket/models")
    location = filt.upload("artifacts/model.bin", BytesIO(b"model-weights"))

    assert location == "s3://demo-bucket/models/artifacts/model.bin"
    fake_fs.open.assert_called_with(
        "demo-bucket/models/artifacts/model.bin",
        "wb",
    )
    assert buffer.getvalue() == b"model-weights"
