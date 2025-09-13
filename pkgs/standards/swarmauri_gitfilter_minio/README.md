<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_gitfilter_minio/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_gitfilter_minio" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_gitfilter_minio/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_gitfilter_minio.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_gitfilter_minio/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_gitfilter_minio" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_gitfilter_minio/">
        <img src="https://img.shields.io/pypi/l/swarmauri_gitfilter_minio" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_gitfilter_minio/">
        <img src="https://img.shields.io/pypi/v/swarmauri_gitfilter_minio?label=swarmauri_gitfilter_minio&color=green" alt="PyPI - swarmauri_gitfilter_minio"/>
    </a>
</p>

---

# Swarmauri Git Filter Minio

Git filter using MinIO or S3 compatible storage.

`swarmauri_gitfilter_minio` provides a storage adapter and Git filter that
stores repository objects in a remote MinIO (or any S3 compatible) service.
It is commonly used by the [`peagen`](https://pypi.org/project/peagen/) tool to
offload large files from source control, but it can also be integrated directly
into applications that need simple object storage.

## Installation

```bash
pip install swarmauri_gitfilter_minio
```

## Configuration

The filter reads credentials from either a `peagen.toml` configuration file or
the `MINIO_ACCESS_KEY` and `MINIO_SECRET_KEY` environment variables. The bucket
specified in the URI will be created automatically if it does not already
exist.

## Usage

```python
from swarmauri_gitfilter_minio import MinioFilter

# Create a filter from a connection string. The scheme `minios://` will use
# HTTPS while `minio://` uses plain HTTP.
filt = MinioFilter.from_uri("minio://localhost:9000/my-bucket/prefix")

# Upload a file and retrieve its URI
with open("README.md", "rb") as fh:
    uri = filt.upload("docs/README.md", fh)

# Download the file back into memory
buffer = filt.download("docs/README.md")
data = buffer.read()
```

`MinioFilter` also exposes helpers such as `upload_dir` and `download_prefix`
for working with entire directory trees.
