![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_prompt_j2prompttemplate/">
        <img src="https://static.pepy.tech/badge/swarmauri_prompt_j2prompttemplate/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_prompt_j2prompttemplate/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_prompt_j2prompttemplate.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_prompt_j2prompttemplate/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_prompt_j2prompttemplate/">
        <img src="https://img.shields.io/pypi/l/swarmauri_prompt_j2prompttemplate" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_prompt_j2prompttemplate/">
        <img src="https://img.shields.io/pypi/v/swarmauri_prompt_j2prompttemplate?label=swarmauri_prompt_j2prompttemplate&color=green" alt="PyPI - swarmauri_prompt_j2prompttemplate"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Prompt J2PromptTemplate

`J2PromptTemplate` is the Swarmauri Jinja2 prompt template implementation. It
accepts literal template strings or template files, renders them with the
variables you provide, and registers itself as the `J2PromptTemplate`
`swarmauri.prompts` entry point.

## Highlights

- Load template content from inline strings or filesystem paths.
- Configure one or more search directories via `templates_dir` for reusable
  Jinja2 templates with fallback lookup.
- Ship with helpful filters (`split`, `make_singular`, `make_plural`) for prompt
  engineering tasks.
- Render in Jinja's sandbox by default so template source cannot traverse the
  Python object graph or invoke unsafe callables.
- Call the instance directly (`template({...})`) or use `generate_prompt()` to
  render with the stored variables.

## Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_prompt_j2prompttemplate

# Poetry
poetry add swarmauri_prompt_j2prompttemplate

# uv
uv add swarmauri_prompt_j2prompttemplate
```

## Usage

### Render a template string

```python
from swarmauri_prompt_j2prompttemplate import J2PromptTemplate

template = J2PromptTemplate(template="Hello, {{ name }}!")
result = template({"name": "World"})
print(result)  # Hello, World!
```

### Load templates from disk (with filters and search paths)

```python
from pathlib import Path

from swarmauri_prompt_j2prompttemplate import J2PromptTemplate

templates_dir = Path("templates")
templates_dir.mkdir(parents=True, exist_ok=True)

template_path = templates_dir / "greeting.j2"
template_path.write_text("Hello, {{ animal|make_plural }}!", encoding="utf-8")

prompt = J2PromptTemplate(templates_dir=str(templates_dir))
prompt.set_template(template_path)

print(prompt({"animal": "fox"}))  # Hello, foxes!
```

`set_template()` loads the file with the configured environment. The template
file is located relative to the provided `templates_dir`. If the loader cannot
find it immediately, the class searches recursively before falling back to the
template's own directory.

### Template trust and sandboxing

`J2PromptTemplate` uses `SandboxedEnvironment` by default. Use this mode for
template strings and files that may come from users, registries, generated
artifacts, or any source that is not fully controlled by the application.

Applications that intentionally rely on unrestricted Jinja behavior can opt
in explicitly:

```python
trusted = J2PromptTemplate(
    template="{{ trusted_helper() }}",
    trusted_templates=True,
)
```

Trusted mode allows templates to access the same Python capabilities as a
normal Jinja `Environment`; never enable it for untrusted template source.
Precompiled templates created by a normal Jinja environment are rejected in
the default mode because they cannot be retroactively sandboxed. The sandbox
limits Python object access, but applications should still apply time and
resource limits when rendering adversarial templates.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) that will help you get started.


