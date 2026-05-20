![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/tigrbl-orm/">
        <img src="https://static.pepy.tech/badge/tigrbl-orm/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/tigrbl_orm/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/tigrbl_orm.svg"/></a>
    <a href="https://pypi.org/project/tigrbl-orm/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/tigrbl-orm/">
        <img src="https://img.shields.io/pypi/l/tigrbl-orm" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/tigrbl-orm/">
        <img src="https://img.shields.io/pypi/v/tigrbl-orm?label=tigrbl-orm&color=green" alt="PyPI - tigrbl-orm"/></a>
</p>
---

# tigrbl-orm

![PyPI - Downloads](https://static.pepy.tech/badge/tigrbl-orm/month) ![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg) ![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue) ![License](https://img.shields.io/pypi/l/tigrbl-orm.svg) ![Version](https://img.shields.io/pypi/v/tigrbl-orm.svg)

## Features

- Provides the `tigrbl_orm.orm` module as a standalone package.
- Includes reusable ORM mixins and table models for Tigrbl services.
- Supports Python 3.10 through 3.12.

## Installation

### uv

```bash
uv add tigrbl-orm
```

### pip

```bash
pip install tigrbl-orm
```

## Usage

```python
from tigrbl_orm.orm.tables.user import User

print(User.__tablename__)
```

Install this package alongside other Tigrbl components when you need SQLAlchemy-backed models.
