![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://img.shields.io/pypi/dm/pj)](https://pypi.org/project/pj/)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/pj.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/pj/)
[![Python](https://img.shields.io/pypi/pyversions/pj)](https://pypi.org/project/pj/)
[![License](https://img.shields.io/pypi/l/pj)](https://pypi.org/project/pj/)
[![Version](https://img.shields.io/pypi/v/pj?label=pj&color=green)](https://pypi.org/project/pj/)

# pj

Experimental placeholder package in the Swarmauri SDK. This planning-stage release has no functional API and is not intended for production use.

## Features

- Placeholder distribution with version metadata.
- No runtime dependencies or import-time side effects.
- Declares Python 3.10 through 3.15 under Apache-2.0.

## Installation

Install the development release explicitly:

```bash
uv pip install pj==0.0.1.dev1
pip install pj==0.0.1.dev1
```

## Usage

```python
from importlib.metadata import version

print(version("pj"))
```

This release provides version metadata only. Future functionality is not yet specified.

## Contributing

See the [SDK contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md).
