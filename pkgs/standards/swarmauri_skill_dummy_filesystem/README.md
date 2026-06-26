# Swarmauri Dummy FileSystem Skill

![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

DummyFileSystemSkill provides a packaged filesystem-backed skill for Swarmauri tests.

[![PyPI Downloads](https://static.pepy.tech/badge/swarmauri_skill_dummy_filesystem)](https://pepy.tech/projects/swarmauri_skill_dummy_filesystem)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_skill_dummy_filesystem.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_skill_dummy_filesystem/)
[![Python Versions](https://img.shields.io/pypi/pyversions/swarmauri_skill_dummy_filesystem)](https://pypi.org/project/swarmauri_skill_dummy_filesystem/)
[![License](https://img.shields.io/pypi/l/swarmauri_skill_dummy_filesystem)](https://pypi.org/project/swarmauri_skill_dummy_filesystem/)
[![PyPI Version](https://img.shields.io/pypi/v/swarmauri_skill_dummy_filesystem)](https://pypi.org/project/swarmauri_skill_dummy_filesystem/)

## Features

- Provides a concrete Swarmauri skill for tests and examples.
- Loads an included `SKILL.md` package through `FileSystemSkillMixin`.
- Exposes a `swarmauri.skills` entry point for discovery checks.

## Installation

```bash
uv add swarmauri_skill_dummy_filesystem
```

```bash
pip install swarmauri_skill_dummy_filesystem
```

## Usage

```python
from swarmauri_skill_dummy_filesystem import DummyFileSystemSkill

skill = DummyFileSystemSkill.from_default()
print(skill.instructions)
```

## Contributing

This package is part of the Swarmauri SDK monorepo.
