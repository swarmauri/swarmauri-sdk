"""Executable example from the README."""

from contextlib import nullcontext
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from swarmauri_gitfilter_s3fs import S3FSFilter


@pytest.mark.example
def test_readme_usage_example() -> None:
    with patch(
        "swarmauri_gitfilter_s3fs.s3fs_filter.s3fs.S3FileSystem"
    ) as filesystem_cls:
        fake_fs = MagicMock()
        buffer = BytesIO()
        fake_fs.open.return_value = nullcontext(buffer)
        filesystem_cls.return_value = fake_fs

        filt = S3FSFilter.from_uri("s3://demo-bucket/models")
        location = filt.upload("artifacts/model.bin", BytesIO(b"model-weights"))

        assert location == "s3://demo-bucket/models/artifacts/model.bin"
        fake_fs.open.assert_called_with(
            "demo-bucket/models/artifacts/model.bin",
            "wb",
        )
        assert buffer.getvalue() == b"model-weights"
