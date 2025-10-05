from __future__ import annotations
import os
import pytest
from typing import List, Optional

PLUGIN_GROUP = "wcag-pdf-pytest"

def pytest_addoption(parser: object) -> None:
    group = parser.getgroup(PLUGIN_GROUP)
    group.addoption(
        "--wcag-pdf",
        action="append",
        dest="wcag_pdf_paths",
        default=[],
        help="(wcag-pdf-pytest) Path(s) to PDF(s) to evaluate. May be provided multiple times.",
    )
    group.addoption(
        "--wcag-pdf-include-depends",
        action="store_true",
        dest="wcag_pdf_include_depends",
        default=False,
        help="(wcag-pdf-pytest) Include context-dependent criteria.",
    )
    group.addoption(
        "--wcag-pdf-level",
        action="append",
        choices=["A", "AA", "AAA"],
        dest="wcag_pdf_level",
        default=[],
        help="(wcag-pdf-pytest) Restrict tests to WCAG level(s): A, AA, and/or AAA.",
    )

@pytest.fixture(scope="session")
def wcag_pdf_paths(pytestconfig: pytest.Config) -> List[str]:
    paths = pytestconfig.getoption("wcag_pdf_paths") or []
    return [os.path.abspath(os.path.expanduser(p)) for p in paths]

class WCAGContext:
    def __init__(self, include_depends: bool, levels: Optional[List[str]]):
        self.include_depends = include_depends
        self.levels = levels or []

@pytest.fixture(scope="session")
def wcag_context(pytestconfig: pytest.Config) -> "WCAGContext":
    return WCAGContext(
        include_depends=pytestconfig.getoption("wcag_pdf_include_depends"),
        levels=pytestconfig.getoption("wcag_pdf_level"),
    )
