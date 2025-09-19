![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/peagen_templset_vue/">
        <img src="https://img.shields.io/pypi/dm/peagen_templset_vue" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/peagen_templset_vue/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/peagen_templset_vue.svg"/></a>
    <a href="https://pypi.org/project/peagen_templset_vue/">
        <img src="https://img.shields.io/pypi/pyversions/peagen_templset_vue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/peagen_templset_vue/">
        <img src="https://img.shields.io/pypi/l/peagen_templset_vue" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/peagen_templset_vue/">
        <img src="https://img.shields.io/pypi/v/peagen_templset_vue?label=peagen_templset_vue&color=green" alt="PyPI - peagen_templset_vue"/></a>

</p>

---

# `peagen_templset_vue`

`peagen_templset_vue` packages a Peagen template set that scaffolds Vue single-file components (SFCs) with a full suite of supporting assets. The template set is registered under the `peagen.template_sets` entry-point group so the Peagen CLI can discover it automatically after installation.

## Overview

- **Opinionated Vue atoms** – `ptree.yaml.j2` renders a component folder containing an `index.ts` barrel, the Vue SFC, scoped CSS, and a generated `*.d.ts` interface file.
- **Comprehensive testing prompts** – the template tree includes Jest/Vitest-ready unit tests, dedicated accessibility and visual regression specs, plus Storybook `.stories.ts` and `.stories.mdx` documents.
- **Accessible defaults** – `agent_default.j2` instructs the LLM to prefer TypeScript, provide docstrings, enforce ARIA annotations, and respect WCAG guidance. Project/module extras such as `REQUIREMENTS`, `STATES`, and `DEPENDENCIES` in your Peagen payload are injected directly into that prompt.
- **Dependency-aware rendering** – each generated file declares its local dependencies so Peagen can order rendering and feed context into the prompts for downstream files.

## Installation

Install the template set alongside the Peagen CLI:

```bash
pip install peagen peagen_templset_vue
# or install the template set into an existing environment
pip install peagen_templset_vue
```

Using Poetry:

```bash
poetry add peagen peagen_templset_vue
# or
poetry add peagen_templset_vue
```

Using [`uv`](https://github.com/astral-sh/uv):

```bash
uv pip install peagen peagen_templset_vue
```

## Example: Inspect the bundled templates

After installation you can programmatically explore the template tree before invoking Peagen. The snippet below locates the packaged resources and prints the key prompts that Peagen will feed into its generation pipeline.

```python
from importlib import resources

package = resources.files("peagen_templset_vue.templates.peagen_templset_vue")
with resources.as_file(package) as template_root:
    top_level = sorted(path.name for path in template_root.glob("*.j2"))
    component_dir = template_root / "{{ PKG.NAME }}" / "src" / "components" / "{{ MOD.NAME }}"
    component_files = [
        entry.name for entry in sorted(component_dir.iterdir(), key=lambda path: path.name)
    ]

    print(f"Template root: {template_root.name}")
    print(f"Top-level prompts: {top_level}")
    print("Component template files:")
    for name in component_files:
        print(f"- {name}")
```

The output highlights the top-level `agent_default.j2` prompt plus every Vue component artefact Peagen will scaffold (Vue SFC, TypeScript barrel, CSS, tests, and Storybook stories).

## Want to help?

If you want to contribute to swarmauri-sdk, read our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md).
