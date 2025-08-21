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
