# PackageMaintenanceAgent

![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_agent_package_maintenance)](https://pepy.tech/projects/swarmauri_agent_package_maintenance)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_agent_package_maintenance.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_agent_package_maintenance)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_agent_package_maintenance)](https://pypi.org/project/swarmauri_agent_package_maintenance/)
[![License](https://img.shields.io/pypi/l/swarmauri_agent_package_maintenance)](LICENSE)
[![Release](https://img.shields.io/pypi/v/swarmauri_agent_package_maintenance?label=swarmauri_agent_package_maintenance&color=green)](https://pypi.org/project/swarmauri_agent_package_maintenance/)

Compose human input, skills, and container checks for SDK maintenance.

## Features

- Compose human input, skills, and container checks for SDK maintenance.
- Supports Python 3.10 through 3.12.

## Installation

```sh
uv add swarmauri_agent_package_maintenance
pip install swarmauri_agent_package_maintenance
```

## Usage

```python
from swarmauri_agent_package_maintenance import PackageMaintenanceAgent
from swarmauri_agent_runner import SqliteRunStore
from swarmauri_base.skills.SkillCatalog import SkillCatalog
from swarmauri_standard.tool_llms.OpenAIToolModel import OpenAIToolModel
from swarmauri_toolkit_containertoolkit import ContainerToolkit

agent = PackageMaintenanceAgent(
    llm=OpenAIToolModel(api_key="your-api-key"),
    store=SqliteRunStore("maintenance.db"),
    skills=SkillCatalog([]),
    container=ContainerToolkit(container_name="sdk-checks"),
    repository_scope="sdk-checks",
    members={"swarmauri_core": "pkgs/core"},
)
# Mount the SDK checkout as /workspace in the configured container first.
state = agent.exec("Ask which package I want to check.")
```

The configured Linux workspace needs Python 3, uv, and the SDK checkout.
Provide an output callback to receive check output as it arrives. The agent
requests approval before formatting, applying lint fixes, running arbitrary
commands, writing process input, or creating a pull request. Recipes dispatch
individual steps through the runner policy. Steps requiring approval can
be invoked directly as separate tool calls.
