# Swarmauri Dummy Local Skill

![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

DummyLocalSkill provides a packaged local skill for Swarmauri tests.

[![PyPI Downloads](https://static.pepy.tech/badge/swarmauri_skill_dummy_local)](https://pepy.tech/projects/swarmauri_skill_dummy_local)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_skill_dummy_local.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_skill_dummy_local/)
[![Python Versions](https://img.shields.io/pypi/pyversions/swarmauri_skill_dummy_local)](https://pypi.org/project/swarmauri_skill_dummy_local/)
[![License](https://img.shields.io/pypi/l/swarmauri_skill_dummy_local)](https://pypi.org/project/swarmauri_skill_dummy_local/)
[![PyPI Version](https://img.shields.io/pypi/v/swarmauri_skill_dummy_local)](https://pypi.org/project/swarmauri_skill_dummy_local/)

## Features

- Provides a concrete Swarmauri skill for tests and examples.
- Loads an included named local skill through `LocalSkillMixin`.
- Exposes a `swarmauri.skills` entry point for discovery checks.

## Installation

```bash
uv add swarmauri_skill_dummy_local
```

```bash
pip install swarmauri_skill_dummy_local
```

## Usage

```python
from swarmauri_skill_dummy_local import DummyLocalSkill

skill = DummyLocalSkill.from_default()
print(skill.skill_name)
```

## Contributing

This package is part of the Swarmauri SDK monorepo.
