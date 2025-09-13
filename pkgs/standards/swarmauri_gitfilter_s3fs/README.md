<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

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

S3 backed git filter for Peagen using ``s3fs``.

## Installation

```bash
pip install swarmauri_gitfilter_s3fs
```

## Usage

```python
from swarmauri_gitfilter_s3fs import S3FSFilter

filt = S3FSFilter.from_uri("s3://bucket/path")
```
