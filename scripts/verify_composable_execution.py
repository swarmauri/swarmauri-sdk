"""Run focused package-isolated checks for the composable runtime.

Use a Python 3.10-3.12 virtual environment with uv on PATH. Install the selected
workspace members listed below editable and with --no-deps, then install:
pydantic pyyaml toml numpy httpx starlette jsonschema cryptography PyJWT
poetry-core pytest pytest-asyncio pytest-timeout pytest-mock pytest-json-report
python-dotenv pyppeteer ruff==0.15.21

Editable support members: core, base, typing, swarmauri_standard, swarmauri;
standards/swarmauri_agent_runner, swarmauri_runstore_sqlite,
swarmauri_tool_askuser, swarmauri_tokens_jwt, swarmauri_keyprovider_local,
swarmauri_transport_httpx, swarmauri_signing_jws, swarmauri_signing_hmac,
swarmauri_signing_rsa, swarmauri_signing_ecdsa, swarmauri_signing_ed25519;
experimental/swarmauri_workflow_statedriven; and all nine MEMBERS below.

The explicit --no-sync uses these installed workspace revisions rather than
resolving every unrelated provider. On Windows, asyncio needs loopback access.
"""

import os
from pathlib import Path
import subprocess
import sys

MEMBERS = (
    "swarmauri_execution_default",
    "swarmauri_taskmanager_default",
    "swarmauri_taskstore_sqlite",
    "swarmauri_permission_explicit",
    "swarmauri_delegation_attenuating",
    "swarmauri_grantstore_sqlite",
    "swarmauri_invoker_default",
    "swarmauri_workflow_documentassistant",
    "swarmauri_workflow_delegatedresearch",
)


def main():
    root = Path(__file__).resolve().parents[1]
    environment = dict(os.environ)
    environment["UV_PROJECT_ENVIRONMENT"] = sys.prefix
    for member in MEMBERS:
        subprocess.run(
            [
                "uv",
                "run",
                "--no-sync",
                "--directory",
                str(root / "pkgs" / "standards" / member),
                "--package",
                member,
                "pytest",
                "-q",
                "-o",
                "asyncio_mode=auto",
            ],
            check=True,
            env=environment,
            cwd=root,
        )


if __name__ == "__main__":
    main()
