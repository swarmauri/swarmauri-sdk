"""Run the maintained TLS workflow tests against checkout source, without service credentials."""

import sys
from pathlib import Path

import pytest


def main():
    root = Path(__file__).resolve().parents[2]
    package = root / "pkgs/40-standards/swarmauri_transport_tls_unicast"
    sys.path[:0] = [
        str(root / path)
        for path in (
            "pkgs/20-bases/swarmauri_base",
            "pkgs/10-interfaces/swarmauri_core",
            "pkgs/00-typing/swarmauri_typing",
            "pkgs/40-standards/swarmauri_transport_tls_unicast",
        )
    ]
    return pytest.main(
        [
            str(package / "tests/test_tls_unicast_transport.py"),
            str(package / "tests/unit/test_readme_workflows.py"),
            "--confcutdir=" + str(package / "tests"),
            "-c",
            str(package / "pyproject.toml"),
            "-q",
            *sys.argv[1:],
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
