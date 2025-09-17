![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_prompt_j2prompttemplate/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_prompt_j2prompttemplate" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_prompt_j2prompttemplate/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_prompt_j2prompttemplate.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_prompt_j2prompttemplate/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_prompt_j2prompttemplate" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_prompt_j2prompttemplate/">
        <img src="https://img.shields.io/pypi/l/swarmauri_prompt_j2prompttemplate" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_prompt_j2prompttemplate/">
        <img src="https://img.shields.io/pypi/v/swarmauri_prompt_j2prompttemplate?label=swarmauri_prompt_j2prompttemplate&color=green" alt="PyPI - swarmauri_prompt_j2prompttemplate"/></a>
</p>

---

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

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) that will help you get started.
