from __future__ import annotations

from tigrbl_core._spec.binding_spec import (
    BindingRegistrySpec,
    BindingSpec,
    HttpRestBindingSpec,
    resolve_rest_nested_prefix,
)
from tigrbl_core.config.constants import TIGRBL_NESTED_PATHS_ATTR


def test_binding_registry_register_get_and_values() -> None:
    binding = BindingSpec(
        name="list_items",
        spec=HttpRestBindingSpec(proto="http.rest", methods=("GET",), path="/items"),
    )
    registry = BindingRegistrySpec()

    registry.register(binding)

    assert registry.get("list_items") == binding
    assert registry.values() == (binding,)


def test_resolve_rest_nested_prefix_prefers_callable_attr() -> None:
    class Model:
        _nested_path = "/fallback"

        @staticmethod
        def nested_path() -> str:
            return "/callable"

    setattr(Model, TIGRBL_NESTED_PATHS_ATTR, Model.nested_path)

    assert resolve_rest_nested_prefix(Model) == "/callable"
