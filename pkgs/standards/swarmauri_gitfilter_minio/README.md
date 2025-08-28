![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri-gitfilter-minio/">
        <img src="https://img.shields.io/pypi/dm/swarmauri-gitfilter-minio" alt="PyPI - Downloads"/>
    </a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/standards/swarmauri_gitfilter_minio">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/standards/swarmauri_gitfilter_minio&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-gitfilter-minio/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri-gitfilter-minio" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-gitfilter-minio/">
        <img src="https://img.shields.io/pypi/l/swarmauri-gitfilter-minio" alt="PyPI - License"/>
    </a>
    <br />
    <a href="https://pypi.org/project/swarmauri-gitfilter-minio/">
        <img src="https://img.shields.io/pypi/v/swarmauri-gitfilter-minio?label=swarmauri-gitfilter-minio&color=green" alt="PyPI - swarmauri-gitfilter-minio"/>
    </a>
</p>

---

# `swarmauri-gitfilter-minio`

MinIO-backed git filter for Peagen.

## Installation

This package is part of the Swarmauri SDK monorepo.

## Usage

```python
from swarmauri_gitfilter_minio import MinioFilter

flt = MinioFilter.from_uri("s3://localhost:9000/peagen")
```
