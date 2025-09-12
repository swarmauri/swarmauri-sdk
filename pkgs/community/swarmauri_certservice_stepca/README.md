![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_certservice_stepca/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certservice_stepca" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_stepca/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_stepca.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_stepca/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certservice_stepca" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_stepca/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certservice_stepca" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_stepca/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certservice_stepca?label=swarmauri_certservice_stepca&color=green" alt="PyPI - swarmauri_certservice_stepca"/></a>

</p>

---

# Swarmauri Step-ca Certificate Service

Community plugin providing a step-ca backed certificate service for Swarmauri.

## Features
- Create CSRs following [RFC 2986](https://datatracker.ietf.org/doc/html/rfc2986)
- Handle X.509 certificates per [RFC 5280](https://datatracker.ietf.org/doc/html/rfc5280)

## Installation
```bash
pip install swarmauri_certservice_stepca
```

## Usage
```python
from swarmauri_certservice_stepca import StepCaCertService

service = StepCaCertService("https://ca.example", token_provider=lambda claims: "token")
```
