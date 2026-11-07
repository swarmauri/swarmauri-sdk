# SkillsetToolkit

![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_toolkit_skillset)](https://pepy.tech/projects/swarmauri_toolkit_skillset)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_toolkit_skillset.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_toolkit_skillset)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_toolkit_skillset)](https://pypi.org/project/swarmauri_toolkit_skillset/)
[![License](https://img.shields.io/pypi/l/swarmauri_toolkit_skillset)](LICENSE)
[![Release](https://img.shields.io/pypi/v/swarmauri_toolkit_skillset?label=swarmauri_toolkit_skillset&color=green)](https://pypi.org/project/swarmauri_toolkit_skillset/)

Compose tools that discover, activate, and read agent skills.

## Features

- Compose tools that discover, activate, and read agent skills.
- Supports Python 3.10 through 3.12.

## Installation

```sh
uv add swarmauri_toolkit_skillset
pip install swarmauri_toolkit_skillset
```

## Usage

```python
from swarmauri_base.skills.SkillCatalog import SkillCatalog
from swarmauri_toolkit_skillset import SkillsetToolkit

toolkit = SkillsetToolkit(catalog=SkillCatalog([]))
print(toolkit.get_tool_by_name("ListSkills")())
```
