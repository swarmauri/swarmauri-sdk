![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_program_s3fs/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_program_s3fs" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_program_s3fs/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_program_s3fs.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_program_s3fs/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_program_s3fs" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_program_s3fs/">
        <img src="https://img.shields.io/pypi/l/swarmauri_program_s3fs" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_program_s3fs/">
        <img src="https://img.shields.io/pypi/v/swarmauri_program_s3fs?label=swarmauri_program_s3fs&color=green" alt="PyPI - swarmauri_program_s3fs"/></a>
</p>

---

# Swarmauri Program S3fs

Program representation that stores and retrieves source files from S3 using `s3fs`.

## Installation

```bash
pip install swarmauri_program_s3fs
```

## Usage

```python
from swarmauri_program_s3fs import S3fsProgram

program = S3fsProgram.from_s3(bucket="my-bucket", prefix="my-program")
program.save_to_s3(bucket="backup-bucket", prefix="backup")
```
