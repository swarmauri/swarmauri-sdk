# Home Install

The repo marketplace is the source of truth. To install or refresh the plugin in the current Codex home, run the installer from the repository root:

```bash
python plugins/swarmauri-sdk-authoring/scripts/install_home.py
```

The installer uses the Codex CLI to run the same operations a manual install should use:

```bash
codex plugin marketplace add <repo-root>
codex plugin add swarmauri-sdk-authoring@swarmauri-sdk
```

The installer finds the Codex CLI from `CODEX_CLI_PATH` first, then from `PATH`. It registers `<repo-root>/.agents/plugins/marketplace.json` as the `swarmauri-sdk` marketplace and installs `swarmauri-sdk-authoring@swarmauri-sdk` into the local Codex plugin cache. Shared plugin files must use `$CODEX_HOME`, `~`, or relative paths in documentation; never commit workstation-specific absolute paths.
