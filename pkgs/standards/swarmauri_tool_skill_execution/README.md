# Swarmauri Skill Execution Tool

![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

SkillExecutionTool runs skill-local argv command arrays and returns structured subprocess results.

[![PyPI Downloads](https://static.pepy.tech/badge/swarmauri_tool_skill_execution)](https://pepy.tech/projects/swarmauri_tool_skill_execution)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_skill_execution.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_skill_execution/)
[![Python Versions](https://img.shields.io/pypi/pyversions/swarmauri_tool_skill_execution)](https://pypi.org/project/swarmauri_tool_skill_execution/)
[![License](https://img.shields.io/pypi/l/swarmauri_tool_skill_execution)](https://pypi.org/project/swarmauri_tool_skill_execution/)
[![PyPI Version](https://img.shields.io/pypi/v/swarmauri_tool_skill_execution)](https://pypi.org/project/swarmauri_tool_skill_execution/)

## Features

- Provides a single Swarmauri tool for skill-local subprocess execution.
- Accepts one or more commands as argv arrays.
- Runs commands relative to the selected skill root without shell expansion.
- Returns stdout, stderr, exit code, argv, and duration for each command.

## Installation

```bash
uv add swarmauri_tool_skill_execution
```

```bash
pip install swarmauri_tool_skill_execution
```

## Usage

```python
from swarmauri_skill_dummy_filesystem import DummyFileSystemSkill
from swarmauri_tool_skill_execution import SkillExecutionTool

skill = DummyFileSystemSkill.from_default()
tool = SkillExecutionTool(skills=[skill])
result = tool(skill.name, [["python", "scripts/check.py"]])
print(result["results"][0]["stdout"])
```

## Contributing

This package is part of the Swarmauri SDK monorepo.
