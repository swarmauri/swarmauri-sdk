# Home Install

The repo plugin is the source of truth. To mirror it into a local Codex home install, run the installer from the repository root:

```bash
python plugins/swarmauri-sdk-authoring/scripts/install_home.py
```

The installer chooses the home root as:

1. `$CODEX_HOME` when set.
2. `~/.codex` otherwise.

It copies this plugin to `<home>/plugins/swarmauri-sdk-authoring` and updates `<home>/.agents/plugins/marketplace.json` with a local marketplace entry. Shared plugin files must use `$CODEX_HOME`, `~`, or relative paths in documentation; never commit workstation-specific absolute paths.
