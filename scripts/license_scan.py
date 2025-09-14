#!/usr/bin/env -S uv run
# /// script
# dependencies = ["pip-licenses"]
# ///
"""Scan project dependencies and validate licences.

This script runs ``pip-licenses`` to generate a CSV report of all installed
packages and their licences. It fails if any package uses a GPL or AGPL
licence and optionally generates a Trivy SBOM if the ``trivy`` binary is
available on the system.
"""

from __future__ import annotations

import csv
import shutil
import subprocess
import sys
from io import StringIO
from pathlib import Path


def run_pip_licenses() -> str:
    """Return CSV output from ``pip-licenses``."""
    try:
        return subprocess.check_output(["pip-licenses", "--format=csv"], text=True)
    except FileNotFoundError as exc:
        raise RuntimeError(
            "pip-licenses is required; run this script with 'uv run' to install it."
        ) from exc


def check_for_gpl(csv_text: str) -> list[str]:
    """Return packages with GPL or AGPL licences."""
    reader = csv.DictReader(StringIO(csv_text))
    bad: list[str] = []
    for row in reader:
        license_name = (row.get("License") or "").lower()
        if "gpl" in license_name and "lgpl" not in license_name:
            bad.append(f"{row.get('Name')} ({row.get('License')})")
    return bad


def maybe_generate_sbom() -> None:
    """Generate an SPDX SBOM using Trivy if available."""
    if shutil.which("trivy") is None:
        return

    output = Path("sbom.spdx")
    try:
        subprocess.run(
            ["trivy", "fs", "--format", "spdx", "--output", str(output), "."],
            check=True,
        )
        print(f"SBOM written to {output}")
    except subprocess.CalledProcessError as exc:
        print(f"Trivy failed: {exc}", file=sys.stderr)


def main() -> None:
    csv_text = run_pip_licenses()
    print(csv_text)
    offending = check_for_gpl(csv_text)
    if offending:
        print("Disallowed licences found:")
        for pkg in offending:
            print(f"  - {pkg}")
        sys.exit(1)

    maybe_generate_sbom()


if __name__ == "__main__":
    main()
