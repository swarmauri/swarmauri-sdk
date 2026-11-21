"""Execute the maintained source rendered into the README quick start."""

from pathlib import Path
from runpy import run_path

import pytest


QUICK_START = (
    Path(__file__).resolve().parents[2] / "docs/readme/quick_start.py"
)


@pytest.mark.example
def test_readme_quickstart_example_runs() -> None:
    certificate = run_path(str(QUICK_START)).get("certificate_pem")

    assert isinstance(certificate, bytes)
    assert certificate.startswith(b"-----BEGIN CERTIFICATE-----")
