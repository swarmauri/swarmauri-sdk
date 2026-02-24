"""Lesson 08.4: Registering JSON-RPC callables."""

from tigrbl import Base, bind, register_rpc
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_register_rpc_returns_router():
    """Explain that RPC registration attaches a `rpc` namespace on the model.

    Purpose: show that registering RPC callables creates a predictable location
    for JSON-RPC method implementations.
    Design practice: keep RPC registration centralized to avoid drift.
    """

    # Setup: declare a model to register RPC callables against.
    class LessonRPCBind(Base, GUIDPk):
        __tablename__ = "lesson_rpc_bind"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    # Deployment: bind ops and register RPC callables.
    specs = bind(LessonRPCBind)
    register_rpc(LessonRPCBind, specs)

    # Assertion: the RPC namespace is created on the model.
    assert hasattr(LessonRPCBind, "rpc")


def test_register_rpc_exposes_list_callable():
    """Confirm that canonical ops are exposed as RPC callables.

    Purpose: verify that the `list` operation can be invoked through RPC.
    Design practice: align RPC exposure with REST operations for parity.
    """

    # Setup: define a model with default ops for RPC exposure.
    class LessonRPCBindList(Base, GUIDPk):
        __tablename__ = "lesson_rpc_bind_list"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    # Deployment: bind ops and register RPC callables.
    specs = bind(LessonRPCBindList)
    register_rpc(LessonRPCBindList, specs)

    # Assertion: default list operation is available for RPC calls.
    assert hasattr(LessonRPCBindList.rpc, "list")
