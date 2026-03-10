from __future__ import annotations

from types import SimpleNamespace

import pytest

import tigrbl_canon.mapping as mapping


@pytest.mark.parametrize(
    ("attr_name", "module_name", "module_attr"),
    [
        ("bind", ".model", "bind"),
        ("rebind", ".model", "rebind"),
        ("build_schemas", ".schemas", "build_and_attach"),
        ("build_hooks", ".hooks", "normalize_and_attach"),
        ("build_handlers", ".handlers", "build_and_attach"),
        ("register_rpc", ".rpc", "register_and_attach"),
        ("build_rest", ".rest", "build_router_and_attach"),
        ("bind_response", ".responses_resolver", "resolve_response_spec"),
        ("include_table", ".router.include", "include_table"),
        ("include_tables", ".router.include", "include_tables"),
        ("rpc_call", ".router.rpc", "rpc_call"),
        ("collect", ".traversal", "collect"),
        ("install", ".traversal", "install"),
    ],
)
def test_mapping_lazy_exports_resolve_from_expected_modules(
    monkeypatch: pytest.MonkeyPatch,
    attr_name: str,
    module_name: str,
    module_attr: str,
) -> None:
    sentinel = object()

    def fake_import(name: str, package: str):
        assert package == "tigrbl_canon.mapping"
        assert name == module_name
        return SimpleNamespace(**{module_attr: sentinel})

    monkeypatch.setattr(mapping, "import_module", fake_import)

    assert getattr(mapping, attr_name) is sentinel


def test_mapping_unknown_export_raises_attribute_error() -> None:
    with pytest.raises(AttributeError, match="unknown_export"):
        getattr(mapping, "unknown_export")
