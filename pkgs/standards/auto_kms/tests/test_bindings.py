from __future__ import annotations

import pathlib
import sys
import types
from unittest.mock import patch


def _ensure_autoapi_namespace() -> None:
    pkgs = pathlib.Path(__file__).resolve().parents[3]
    autoapi_root = pkgs / "standards" / "autoapi" / "autoapi"

    autoapi_pkg = types.ModuleType("autoapi")
    autoapi_pkg.__path__ = [str(autoapi_root)]
    sys.modules.setdefault("autoapi", autoapi_pkg)

    v3_pkg = types.ModuleType("autoapi.v3")
    v3_pkg.__path__ = [str(autoapi_root / "v3")]
    sys.modules.setdefault("autoapi.v3", v3_pkg)


def test_key_bindings_available_before_mount() -> None:
    _ensure_autoapi_namespace()
    from standards.auto_kms.auto_kms.tables.key import Key
    from autoapi.v3.bindings import model as model_binding

    with patch(
        "autoapi.v3.bindings.model._rest_binding.build_router_and_attach",
        lambda model, specs, only_keys=None: None,
    ):
        model_binding.bind(Key)

    assert callable(Key.rpc.create)
    assert hasattr(Key.hooks, "create")


def test_key_version_bindings_available_before_mount() -> None:
    _ensure_autoapi_namespace()
    from standards.auto_kms.auto_kms.tables.key_version import KeyVersion
    from autoapi.v3.bindings import model as model_binding

    with patch(
        "autoapi.v3.bindings.model._rest_binding.build_router_and_attach",
        lambda model, specs, only_keys=None: None,
    ):
        model_binding.bind(KeyVersion)

    assert callable(KeyVersion.rpc.list)
