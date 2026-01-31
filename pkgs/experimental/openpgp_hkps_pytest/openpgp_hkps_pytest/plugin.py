from __future__ import annotations

import os
from importlib import import_module
from inspect import Parameter, signature
from pathlib import Path
from typing import Iterable, Optional

import httpx
import pytest
import pytest_asyncio

PLUGIN_GROUP = "openpgp-hkps"
BASE_URL_ENV = "HPKS_TEST_BASE_URL"
ARMORED_ENV = "HPKS_TEST_ARMORED"
BINARY_ENV = "HPKS_TEST_BINARY"
DEFAULT_IMPORT_PATHS = (
    "hpks.app:app",
    "hpks.app:build_app",
    "hpks.main:create_app",
    "app:app",
)


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup(PLUGIN_GROUP)
    group.addoption(
        "--hkps-base-url",
        action="store",
        default=None,
        help="Base URL for a remote HKPS server (overrides HPKS_TEST_BASE_URL).",
    )
    group.addoption(
        "--hkps-armored-path",
        action="store",
        default=None,
        help="Path to an ASCII-armored OpenPGP certificate bundle for /pks/add tests.",
    )
    group.addoption(
        "--hkps-binary-path",
        action="store",
        default=None,
        help="Path to a binary OpenPGP certificate bundle for /pks/v2/add tests.",
    )
    group.addoption(
        "--hkps-app-import",
        action="append",
        dest="hkps_app_imports",
        default=[],
        help=(
            "Additional module:object locations used to resolve an ASGI app when no "
            "--hkps-base-url is provided."
        ),
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "hkps: OpenPGP HKP/HKPS interoperability tests",
    )


def _is_zero_arg_factory(obj: object) -> bool:
    if not callable(obj):
        return False
    try:
        sig = signature(obj)
    except (TypeError, ValueError):
        return False
    for parameter in sig.parameters.values():
        if parameter.kind in (
            Parameter.POSITIONAL_ONLY,
            Parameter.POSITIONAL_OR_KEYWORD,
        ):
            if parameter.default is Parameter.empty:
                return False
        elif (
            parameter.kind == Parameter.KEYWORD_ONLY
            and parameter.default is Parameter.empty
        ):
            return False
    return True


def _load_asgi_app(import_paths: Iterable[str]) -> Optional[object]:
    for import_path in import_paths:
        try:
            module_name, attribute = import_path.split(":", 1)
        except ValueError:
            continue
        try:
            module = import_module(module_name)
            target = getattr(module, attribute)
        except Exception:
            continue
        app = target() if _is_zero_arg_factory(target) else target
        if app is not None:
            return app
    return None


def _build_async_client(config: pytest.Config) -> httpx.AsyncClient:
    base_url = config.getoption("hkps_base_url") or os.getenv(BASE_URL_ENV)
    if base_url:
        return httpx.AsyncClient(base_url=base_url)

    configured_imports = config.getoption("hkps_app_imports") or []
    candidates = list(dict.fromkeys([*configured_imports, *DEFAULT_IMPORT_PATHS]))
    app = _load_asgi_app(candidates)
    if app is None:
        pytest.skip(
            "No HKPS server configured. Provide --hkps-base-url or install an ASGI app."
        )
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://testserver")


def _resolve_bytes(
    config: pytest.Config, option_name: str, env_name: str
) -> Optional[bytes]:
    path = config.getoption(option_name) or os.getenv(env_name)
    if not path:
        return None
    resolved = Path(path).expanduser()
    if not resolved.exists():
        raise pytest.UsageError(f"File not found for {env_name}: {resolved}")
    return resolved.read_bytes()


@pytest_asyncio.fixture(scope="session")
async def hkps_async_client(pytestconfig: pytest.Config) -> httpx.AsyncClient:
    client = _build_async_client(pytestconfig)
    try:
        yield client
    finally:
        await client.aclose()


@pytest.fixture(scope="session")
def hkps_armored_bundle(pytestconfig: pytest.Config) -> Optional[bytes]:
    return _resolve_bytes(pytestconfig, "hkps_armored_path", ARMORED_ENV)


@pytest.fixture(scope="session")
def hkps_binary_bundle(pytestconfig: pytest.Config) -> Optional[bytes]:
    return _resolve_bytes(pytestconfig, "hkps_binary_path", BINARY_ENV)


__all__ = [
    "hkps_async_client",
    "hkps_armored_bundle",
    "hkps_binary_bundle",
]
