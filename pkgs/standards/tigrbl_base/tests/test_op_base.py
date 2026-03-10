from tigrbl_base._base._op_base import OpBase
from tigrbl_core._spec.op_spec import OpSpec


def test_op_base_inheritance() -> None:
    assert issubclass(OpBase, OpSpec)
