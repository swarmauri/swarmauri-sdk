from tigrbl_base._base._binding_base import BindingBase, BindingRegistryBase
from tigrbl_core._spec.binding_spec import BindingRegistrySpec, BindingSpec


def test_binding_base_inheritance() -> None:
    assert issubclass(BindingBase, BindingSpec)
    assert issubclass(BindingRegistryBase, BindingRegistrySpec)
