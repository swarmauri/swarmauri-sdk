# Swarmauri SDK Repo Patterns

Use these rules before changing SDK package surfaces.

## Package Families

- Core interfaces live in `pkgs/core/swarmauri_core`.
- Base classes and mixins live in `pkgs/base/swarmauri_base`.
- Built-in concretes live in `pkgs/swarmauri_standard/swarmauri_standard`.
- First-class standalone packages live in `pkgs/standards`.
- Second-class community packages live in `pkgs/community`.
- Experimental packages live in `pkgs/experimental`.
- Python plugin packages live in `pkgs/plugins`.
- Codex plugins live in top-level `plugins`.

## Metadata

- Require Python `>=3.10,<3.13` and classifiers for Python 3.10, 3.11, and 3.12.
- Use Apache-2.0 licensing.
- For new Swarmauri packages, list only Jacob Stewart `<jacob@swarmauri.com>` as the author.
- Use `Development Status :: 1 - Planning` for new packages unless an existing adjacent package proves a different rule.
- Include a descriptive summary and package-specific keywords.

## Workspace Membership

- Add standalone package members to `pkgs/pyproject.toml` when they should be installed and tested with the workspace.
- Keep entries sorted consistently with the surrounding family block.
- Do not alter unrelated existing workspace entries.

## Validation

Run these from the repository root for every changed package member:

```bash
uv run --directory <member> --package <name> ruff format .
uv run --directory <member> --package <name> ruff check . --fix
uv run --package <name> --directory <member> pytest
```

If `pkgs/swarmauri/swarmauri/interface_registry.py` or `plugin_citizenship_registry.py` changes, also run the focused `pkgs/swarmauri` registry tests.
