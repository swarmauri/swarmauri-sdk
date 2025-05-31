![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_program_memorys3fs/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_program_memorys3fs" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_program_memorys3fs/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_program_memorys3fs.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_program_memorys3fs/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_program_memorys3fs" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_program_memorys3fs/">
        <img src="https://img.shields.io/pypi/l/swarmauri_program_memorys3fs" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_program_memorys3fs/">
        <img src="https://img.shields.io/pypi/v/swarmauri_program_memorys3fs?label=swarmauri_program_memorys3fs&color=green" alt="PyPI - swarmauri_program_memorys3fs"/></a>
</p>

---

# Swarmauri Program MemoryS3FS

In-memory S3 filesystem based program implementation using `s3fs` and `fsspec`.

## Installation

```bash
pip install swarmauri_program_memorys3fs
```

## Usage

```python
from swarmauri_program_memorys3fs import MemoryS3FSProgram

program = MemoryS3FSProgram()
program.content["hello.py"] = "print('hi')"
program.save_to_s3(bucket="my-bucket", prefix="my-prefix")
```
