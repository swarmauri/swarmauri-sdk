from __future__ import annotations

from pathlib import Path
import tomllib

from ..transport_dependency_helpers import (
    _transport_requirements_from_distribution,
    assert_transport_dependency_parity,
)


PACKAGE_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = PACKAGE_ROOT / "pyproject.toml"
TRANSPORT_PACKAGE = "swarmauri_transport_asgi"


def _load_optional_dependencies() -> dict[str, list[str]]:
    data = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    return data["project"]["optional-dependencies"]


def test_httpx_transport_parity_asgi():
    assert_transport_dependency_parity(
        transport_package=TRANSPORT_PACKAGE,
        parity_distribution_name="httpx",
    )


def test_asgi_transport_listed_in_transports_optional_dependency_group():
    optional_dependencies = _load_optional_dependencies()

    transports_group = optional_dependencies["transports"]
    assert any(dep.startswith(f"{TRANSPORT_PACKAGE}>=") for dep in transports_group)


def test_asgi_transport_has_dedicated_optional_dependency_key():
    optional_dependencies = _load_optional_dependencies()

    assert TRANSPORT_PACKAGE in optional_dependencies
    dedicated_group = optional_dependencies[TRANSPORT_PACKAGE]
    assert dedicated_group == [f"{TRANSPORT_PACKAGE}>=0.1.0"]


def test_asgi_transport_dependency_presence_differs_between_swarmauri_canon_http_and_httpx():
    swarmauri_canon_http_requirements = _transport_requirements_from_distribution(
        "swarmauri_canon_http"
    )
    httpx_requirements = _transport_requirements_from_distribution("httpx")

    assert TRANSPORT_PACKAGE in swarmauri_canon_http_requirements
    assert TRANSPORT_PACKAGE not in httpx_requirements
