#!/usr/bin/env -S uv run
# /// script
# dependencies = ["pip-licenses"]
# ///
"""Scan project dependencies and validate licences.

This script runs ``pip-licenses`` to generate a CSV report of all installed
packages and their licences.  A Markdown summary is written to
``license_report.md`` and the raw CSV output to ``license_report.csv``.

The scan fails if any package uses a GPL or AGPL licence and optionally
generates a Trivy SBOM if the ``trivy`` binary is available on the system.
"""

from __future__ import annotations

import csv
import shutil
import subprocess
import sys
from collections import defaultdict
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


def check_for_gpl(rows: list[dict[str, str]]) -> list[str]:
    """Return packages with GPL or AGPL licences."""

    bad: list[str] = []
    for row in rows:
        license_name = (row.get("License") or "").lower()
        if "gpl" in license_name and "lgpl" not in license_name:
            bad.append(f"{row.get('Name')} ({row.get('License')})")
    return bad


def generate_markdown_report(
    rows: list[dict[str, str]], csv_text: str, offending: list[str]
) -> str:
    """Create a Markdown summary and write report files."""

    counts: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        counts[row.get("License") or "Unknown"].append(row.get("Name") or "")

    lines: list[str] = ["# License Scan Report", "", "## Licence Counts", ""]
    lines.append("| Licence | Count |")
    lines.append("| --- | ---: |")
    for licence, pkgs in sorted(counts.items()):
        lines.append(f"| {licence} | {len(pkgs)} |")

    lines.extend(["", "## Packages", "", "| Package | Licence |", "| --- | --- |"])
    for row in rows:
        lines.append(f"| {row.get('Name')} | {row.get('License')} |")

    if offending:
        lines.extend(["", "## Disallowed licences", ""])
        for pkg in offending:
            lines.append(f"- {pkg}")
    else:
        lines.extend(["", "No disallowed licences found."])

    report = "\n".join(lines) + "\n"
    Path("license_report.md").write_text(report)
    Path("license_report.csv").write_text(csv_text)
    return report


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
    rows = list(csv.DictReader(StringIO(csv_text)))
    offending = check_for_gpl(rows)
    report = generate_markdown_report(rows, csv_text, offending)
    print(report)
    if offending:
        sys.exit(1)

    maybe_generate_sbom()


if __name__ == "__main__":
    main()
