![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/openpgp_hkps_pytest/">
        <img src="https://img.shields.io/pypi/dm/openpgp_hkps_pytest" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/openpgp_hkps_pytest/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/openpgp_hkps_pytest.svg"/></a>
    <a href="https://pypi.org/project/openpgp_hkps_pytest/">
        <img src="https://img.shields.io/pypi/pyversions/openpgp_hkps_pytest" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/openpgp_hkps_pytest/">
        <img src="https://img.shields.io/pypi/l/openpgp_hkps_pytest" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/openpgp_hkps_pytest/">
        <img src="https://img.shields.io/pypi/v/openpgp_hkps_pytest?label=openpgp_hkps_pytest&color=green" alt="PyPI - openpgp_hkps_pytest"/></a>
</p>

---

## Overview

`openpgp_hkps_pytest` is a [pytest](https://docs.pytest.org/) plugin that ships
ready-made compliance tests for OpenPGP HKP/HKPS servers. The suite covers the
legacy HKP behaviors described in draft-gallagher-openpgp-hkp-08 and the
proposed HKP v2 semantics from the same draft. Tests may target a remote HKPS
endpoint or an in-process ASGI application, making it easy to exercise staging
and production servers as part of continuous integration.

## Features

- ✅ Legacy HKP compliance checks for index, get, and add endpoints.
- ✅ HKP v2 JSON, binary bundle, and submission contract validation.
- ✅ Configurable client bootstrap via command-line options or environment
  variables.
- ✅ Works against remote HKPS servers or in-process ASGI apps without
  additional scaffolding.
- ✅ Uses a shared asynchronous HTTPX client to minimize connection overhead.

## Installation

Install with `uv`:

```bash
uv add openpgp_hkps_pytest
```

Install with `pip`:

```bash
pip install openpgp_hkps_pytest
```

`pytest` automatically discovers the plugin through the `pytest11` entry point
once the package is installed.

## Usage

The test suite can run against a deployed HKPS base URL or an ASGI application
importable within the current environment. Invoke pytest with the package name
using `--pyargs`:

```bash
pytest --pyargs openpgp_hkps_pytest
```

### Targeting a Remote Server

Provide a base URL via command-line flag or environment variable:

```bash
pytest --pyargs openpgp_hkps_pytest --hkps-base-url="https://keys.example.com"
```

or set the environment variable before running pytest:

```bash
export HPKS_TEST_BASE_URL="https://keys.example.com"
pytest --pyargs openpgp_hkps_pytest
```

### Targeting an In-Process ASGI Application

When no base URL is supplied the plugin attempts to import an ASGI application
from common module paths:

- `hpks.app:app`
- `hpks.app:build_app`
- `hpks.main:create_app`
- `app:app`

Additional candidates can be supplied with `--hkps-app-import`. The resolved app
is mounted directly into an `httpx.ASGITransport`, keeping the test loop fully
in-process.

### Submitting Test Certificates

Some tests exercise `/pks/add` endpoints. Provide sample certificates to enable
those checks:

- ASCII-armored bundle for legacy HKP: `--hkps-armored-path` or
  `HPKS_TEST_ARMORED`.
- Binary bundle for HKP v2: `--hkps-binary-path` or `HPKS_TEST_BINARY`.

When the files are not supplied the relevant tests are skipped with an
informative message, allowing the rest of the suite to execute.

## License

Licensed under the [Apache 2.0 License](LICENSE).
