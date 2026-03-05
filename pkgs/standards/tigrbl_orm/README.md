![Tigrbl branding](https://github.com/swarmauri/swarmauri-sdk/blob/a170683ecda8ca1c4f912c966d4499649ffb8224/assets/tigrbl.brand.theme.svg)

# tigrbl-orm

![PyPI - Downloads](https://img.shields.io/pypi/dm/tigrbl-orm.svg) ![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg) ![Python Versions](https://img.shields.io/pypi/pyversions/tigrbl-orm.svg) ![License](https://img.shields.io/pypi/l/tigrbl-orm.svg) ![Version](https://img.shields.io/pypi/v/tigrbl-orm.svg)

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
