<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
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

## Installation

```bash
pip install swarmauri_gitfilter_minio
```

## Usage

```python
from swarmauri_gitfilter_minio import MinioFilter

filt = MinioFilter.from_uri("minio://localhost:9000/bucket")
```
