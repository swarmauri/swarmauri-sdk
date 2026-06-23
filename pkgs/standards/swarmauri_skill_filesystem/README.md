# Swarmauri FileSystem Skill

![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

FilesystemSkill loads Swarmauri skill packages from explicit filesystem paths.

[![PyPI Downloads](https://static.pepy.tech/badge/swarmauri_skill_filesystem)](https://pepy.tech/projects/swarmauri_skill_filesystem)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_skill_filesystem.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_skill_filesystem/)
[![Python Versions](https://img.shields.io/pypi/pyversions/swarmauri_skill_filesystem)](https://pypi.org/project/swarmauri_skill_filesystem/)
[![License](https://img.shields.io/pypi/l/swarmauri_skill_filesystem)](https://pypi.org/project/swarmauri_skill_filesystem/)
[![PyPI Version](https://img.shields.io/pypi/v/swarmauri_skill_filesystem)](https://pypi.org/project/swarmauri_skill_filesystem/)

## Features

- Provides a first-class Swarmauri standard component.
- Uses existing Swarmauri core and base contracts.
- Keeps skill and agent composition language-agnostic at the package boundary.

## Installation

```bash
uv add swarmauri_skill_filesystem
```

```bash
pip install swarmauri_skill_filesystem
```

## Usage

```python
from swarmauri_skill_filesystem import FileSystemSkill

skill = FileSystemSkill.from_path("./my-skill")
print(skill.instructions)
```

## Contributing

This package is part of the Swarmauri SDK monorepo.
