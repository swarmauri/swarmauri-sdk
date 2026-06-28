"""Install this Codex plugin from the repository marketplace."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


MARKETPLACE_NAME = "swarmauri-sdk"
PLUGIN_NAME = "swarmauri-sdk-authoring"
PLUGIN_ID = f"{PLUGIN_NAME}@{MARKETPLACE_NAME}"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _codex_executable() -> str:
    configured = os.environ.get("CODEX_CLI_PATH")
    if configured:
        return configured
    discovered = shutil.which("codex")
    if discovered:
        return discovered
    raise RuntimeError(
        "Could not find the Codex CLI. Set CODEX_CLI_PATH or add codex to PATH."
    )


def _run_codex(*args: str) -> None:
    command = [_codex_executable(), *args]
    subprocess.run(command, cwd=_repo_root(), check=True)


def main() -> int:
    repo = _repo_root()
    _run_codex("plugin", "marketplace", "add", str(repo))
    _run_codex("plugin", "add", PLUGIN_ID)
    print(f"Installed {PLUGIN_ID} from {repo}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
