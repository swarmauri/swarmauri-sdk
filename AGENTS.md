# Contribution Guide

Follow these high-level steps when updating this repository:

- **Style and Linting** – run `uv run --directory <member> --package <name> ruff format .` followed by `ruff check . --fix` inside each changed package under `pkgs/`.
- **Tests** – execute tests in isolation from `pkgs/` with `uv run --package <name> --directory <member> pytest`.
- **Documentation and Style** – keep code consistent with [STYLE_GUIDE.md](STYLE_GUIDE.md).
- **Pull Requests** – ensure commits are well described and reference related issues if applicable.
- **Default Branch** – the repository's default branch is `master`.

Changes to the **peagen** package require additional validation steps detailed in
`pkgs/standards/peagen/AGENTS.md`. Plugins should be instantiated directly;
avoid using the ``PluginManager`` unless explicitly directed otherwise.

## Swarmauri & Tigrbl Package Requirements

- All Swarmauri packages must include the Swarmauri SVG branding in their
  `README.md`, the completed badge set (downloads, hits, supported Python
  versions, license, and release version), a dedicated **Features** section,
  installation instructions for both `uv` and `pip`, and usage guidance that
  explains the expected workflows.
- `pyproject.toml` entries for new Swarmauri packages must specify the planning
  development-stage classifier, a descriptive summary, detailed keywords, and
  list Jacob Stewart `<jacob@swarmauri.com>` as an author (do not add the
  Swarmauri organization as a separate author entry).
- Package metadata and documentation must communicate support for Python 3.10
  through 3.12, and classifiers should be added accordingly.
- When working on Tigrbl packages the same rules apply, but swap the branding
  image with the Tigrbl SVG theme.
- Branding asset locations:
  - Swarmauri theme SVG:
    `https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg`
  - Tigrbl theme SVG:
    `https://github.com/swarmauri/swarmauri-sdk/blob/a170683ecda8ca1c4f912c966d4499649ffb8224/assets/tigrbl.brand.theme.svg`
- If you are unsure which branding to use, default to the Swarmauri SVG.

