![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_gitfilter_s3fs/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_gitfilter_s3fs" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_gitfilter_s3fs/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_gitfilter_s3fs.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_gitfilter_s3fs/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_gitfilter_s3fs" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_gitfilter_s3fs/">
        <img src="https://img.shields.io/pypi/l/swarmauri_gitfilter_s3fs" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_gitfilter_s3fs/">
        <img src="https://img.shields.io/pypi/v/swarmauri_gitfilter_s3fs?label=swarmauri_gitfilter_s3fs&color=green" alt="PyPI - swarmauri_gitfilter_s3fs"/>
    </a>
</p>

---

# Swarmauri Git Filter S3FS

Git filter implementation for Peagen that streams artifacts to Amazon S3 (or
S3-compatible services) through ``s3fs``.  The filter registers as a
``StorageAdapter`` named ``S3FSFilter`` and supports the full git clean/smudge
cycle by delegating reads and writes to the configured S3 bucket.

## Features

- Implements :class:`~swarmauri_base.storage.StorageAdapterBase` and
  :class:`~swarmauri_base.git_filters.GitFilterBase` to provide streaming
  ``upload`` and ``download`` operations.
- Recursively uploads local directories via ``upload_dir`` and reconstructs
  prefixes back onto disk with ``download_prefix``.
- Lists existing objects under a prefix with ``iter_prefix`` to back git
  history reconstruction.
- Reads configuration from ``peagen.toml`` (``[storage.filters.s3fs]``) or the
  ``AWS_*`` environment variables when instantiated through
  :meth:`S3FSFilter.from_uri`.

## Installation

Install the package with your preferred Python packaging tool:

```bash
pip install swarmauri_gitfilter_s3fs
```

```bash
poetry add swarmauri_gitfilter_s3fs
```

```bash
uv pip install swarmauri_gitfilter_s3fs
```

## Configuration

Create the filter by supplying your bucket name and optional connection
parameters:

- ``bucket`` – Target bucket name (required).
- ``prefix`` – Optional key prefix to scope uploads.
- ``key`` / ``secret`` – Credentials for the S3 endpoint.  ``SecretStr``
  instances are supported.
- ``endpoint_url`` – Custom S3-compatible endpoint (useful for MinIO or
  LocalStack).
- ``region_name`` – Region for the endpoint.

When using :meth:`S3FSFilter.from_uri`, the URI sets the ``bucket`` and
``prefix`` while credentials are loaded from ``peagen.toml`` at
``[storage.filters.s3fs]`` (``key``, ``secret``, ``endpoint_url``, and
``region``).  Missing configuration falls back to
``AWS_ACCESS_KEY_ID``, ``AWS_SECRET_ACCESS_KEY``, ``AWS_ENDPOINT_URL``, and
``AWS_REGION`` respectively.

## Usage

The example below patches ``s3fs`` with an in-memory stub so it can run without
network access.  The logic mirrors how ``S3FSFilter`` writes data to S3 and
returns the URI of the uploaded object.

```python
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
```

In a production workflow you do not need to patch ``s3fs`` – instantiate the
filter with your credentials and bucket, then use ``clean``/``smudge`` or
``upload``/``download`` to move artifacts between git and S3.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.