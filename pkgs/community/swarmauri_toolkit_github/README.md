![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_toolkit_github/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_toolkit_github" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_toolkit_github/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_toolkit_github.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_github/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_toolkit_github" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_github/">
        <img src="https://img.shields.io/pypi/l/swarmauri_toolkit_github" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_github/">
        <img src="https://img.shields.io/pypi/v/swarmauri_toolkit_github?label=swarmauri_toolkit_github&color=green" alt="PyPI - swarmauri_toolkit_github"/></a>
</p>

---

# Swarmauri Toolkit · GitHub

A Swarmauri toolkit that wraps PyGithub behind Swarmauri’s agent/tool abstractions. Authenticate once and gain access to repository, issue, pull request, branch, and commit helpers—ready for scripted automation or conversational agents.

- Creates a shared GitHub client so every tool call reuses the same token and rate-limit state.
- Normalizes responses into dictionaries so downstream logic can inspect status messages or raw PyGithub payloads.
- Covers common actions (create/list/update/delete) while staying extensible via the `action` parameter on each tool.

## Requirements

- Python 3.10 – 3.13.
- GitHub personal access token (classic or fine-grained) with the scopes your workflow requires. Store it in an environment variable such as `GITHUB_TOKEN`.
- Runtime dependencies (`PyGithub`, `python-dotenv`, and the Swarmauri base/standard packages) install automatically with the toolkit.

## Installation

Choose any of the supported packaging flows; each command resolves transitive dependencies.

**pip**

```bash
pip install swarmauri_toolkit_github
```

**Poetry**

```bash
poetry add swarmauri_toolkit_github
```

**uv**

```bash
# Add to the current project and update uv.lock
uv add swarmauri_toolkit_github

# or install into the active environment without editing pyproject.toml
uv pip install swarmauri_toolkit_github
```

> Tip: `python-dotenv` is imported automatically—drop your token into a local `.env` file (`GITHUB_TOKEN=ghp_...`) for quick experimentation.

## Quick Start

```python
import os
from swarmauri_toolkit_github import GithubToolkit

toolkit = GithubToolkit(api_token=os.environ["GITHUB_TOKEN"])

# List repositories for the authenticated user
repos = toolkit.github_repo_tool(action="list_repos")
print(repos["list_repos"])

# Open a tracking issue
issue = toolkit.github_issue_tool(
    action="create_issue",
    repo_name="owner/example",
    title="Investigate flaky tests",
    body="Logs: https://gist.github.com/..."
)
print(issue["create_issue"])
```

Each sub-tool accepts an `action` argument (see PyGithub docs for additional options) and returns a dictionary keyed by that action for ergonomic unpacking.

## Usage Scenarios

### Automate Release Housekeeping

```python
from swarmauri_toolkit_github import GithubToolkit

toolkit = GithubToolkit(api_token=os.environ["GITHUB_TOKEN"])

# Create a release branch
toolkit.github_branch_tool(
    action="create_branch",
    repo_name="owner/service",
    new_branch="release/v1.4.0",
    source_branch="master"
)

# Cut a changelog commit
toolkit.github_commit_tool(
    action="create_file",
    repo_name="owner/service",
    path="CHANGELOG.md",
    message="Add release notes",
    content="### v1.4.0\n- New features...",
    branch="release/v1.4.0"
)
```

### Drive GitHub From a Swarmauri Agent

```python
from swarmauri_core.agent.Agent import Agent
from swarmauri_core.messages.HumanMessage import HumanMessage
from swarmauri_standard.tools.registry import ToolRegistry
from swarmauri_toolkit_github import GithubToolkit

toolkit = GithubToolkit(api_token=os.environ["GITHUB_TOKEN"])
registry = ToolRegistry()
registry.register(toolkit.github_issue_tool)
registry.register(toolkit.github_pr_tool)

agent = Agent(tool_registry=registry)
response = agent.run(HumanMessage(content="Open a PR from feature/auth to master"))
print(response)
```

Enable conversational workflows that translate natural-language requests into GitHub mutations.

### Triage Issues Nightly

```python
from datetime import datetime, timedelta
from swarmauri_toolkit_github import GithubToolkit

toolkit = GithubToolkit(api_token=os.environ["GITHUB_TOKEN"])
cutoff = datetime.utcnow() - timedelta(days=7)

issues = toolkit.github_issue_tool(
    action="list",
    repo_name="owner/product",
    state="open"
)["list"]

stale = [issue for issue in issues if issue.updated_at < cutoff]
for issue in stale:
    toolkit.github_issue_tool(
        action="create_comment",
        repo_name="owner/product",
        number=issue.number,
        body="Ping! Any update in the last week?"
    )
```

Keep a backlog tidy by automatically nudging stale tickets.

## Troubleshooting

- **`ValueError: Invalid Token or Missing api_token`** – Pass the token explicitly (`GithubToolkit(api_token=...)`) or export `GITHUB_TOKEN` before instantiating the toolkit.
- **PyGithub exception messages** – Most actions bubble up PyGithub errors verbatim (permission issues, missing branches, etc.). Inspect the text in the returned string to resolve scope or naming problems.
- **GitHub rate limits** – PyGithub tracks remaining requests; consider batching actions or sleeping when `Github.get_rate_limit()` indicates low headroom.

## License

`swarmauri_toolkit_github` is released under the Apache 2.0 License. See `LICENSE` for full details.
