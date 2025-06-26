# Contribution Guide

Follow these high-level steps when updating this repository:

- **Style and Linting** – run `uv run --directory <member> --package <name> ruff format .` followed by `ruff check . --fix` inside each changed package under `pkgs/`.
- **Tests** – execute tests in isolation from `pkgs/` with `uv run --package <name> --directory <member> pytest`.
- **Documentation and Style** – keep code consistent with [STYLE_GUIDE.md](STYLE_GUIDE.md).
- **Pull Requests** – ensure commits are well described and reference related issues if applicable.

Changes to the **peagen** package require additional validation steps detailed in
`pkgs/standards/peagen/AGENTS.md`. When modifying plugin code, ensure all
plugins are loaded via the ``PluginManager`` rather than direct imports.

