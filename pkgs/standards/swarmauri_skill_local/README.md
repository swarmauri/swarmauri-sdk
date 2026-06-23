# Swarmauri Local Skill

![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

LocalSkill resolves Swarmauri skills from configured local skill roots.

[![PyPI Downloads](https://static.pepy.tech/badge/swarmauri_skill_local)](https://pepy.tech/projects/swarmauri_skill_local)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_skill_local.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_skill_local/)
[![Python Versions](https://img.shields.io/pypi/pyversions/swarmauri_skill_local)](https://pypi.org/project/swarmauri_skill_local/)
[![License](https://img.shields.io/pypi/l/swarmauri_skill_local)](https://pypi.org/project/swarmauri_skill_local/)
[![PyPI Version](https://img.shields.io/pypi/v/swarmauri_skill_local)](https://pypi.org/project/swarmauri_skill_local/)

## Features

- Provides a first-class Swarmauri standard component.
- Uses existing Swarmauri core and base contracts.
- Keeps skill and agent composition language-agnostic at the package boundary.

## Installation

```bash
uv add swarmauri_skill_local
```

```bash
pip install swarmauri_skill_local
```

## Usage

```python
from swarmauri_skill_local import LocalSkill

skill = LocalSkill.from_name("my-skill", roots=["./skills"])
print(skill.name)
```

## Contributing

This package is part of the Swarmauri SDK monorepo.
