<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


<p align="center">
    <a href="https://pypi.org/project/swarmauri_certservice_scep/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certservice_scep" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_scep/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_scep.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_scep/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certservice_scep" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_scep/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certservice_scep" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_scep/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certservice_scep?label=swarmauri_certservice_scep&color=green" alt="PyPI - swarmauri_certservice_scep"/></a>
</p>

---

# Swarmauri Certservice SCEP

A certificate enrollment service implementing the Simple Certificate Enrollment Protocol (SCEP).

## Installation

```bash
pip install swarmauri_certservice_scep
```

## Usage

```python
from swarmauri_certservice_scep import ScepCertService

service = ScepCertService("https://scep.example.test", challenge_password="secret")
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
