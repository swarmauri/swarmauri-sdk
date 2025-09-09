from tigrbl.v3.autoapp import AutoApp
from tigrbl.v3.bindings.model import bind
from tigrbl.v3.runtime.kernel import _default_kernel as K
from tigrbl.v3.specs import S, IO, acol
from tigrbl.v3.orm.tables import Base
from tigrbl.v3.types import Integer as IntType


def test_compiles_opview_for_new_model_after_prime():
    Base.metadata.clear()

    class A(Base):
        __tablename__ = "kernel_on_demand_a"
        __allow_unmapped__ = True
        id = acol(
            storage=S(type_=IntType, primary_key=True), io=IO(out_verbs=("read",))
        )

    bind(A)
    app = AutoApp()
    app.include_model(A, mount_router=False)
    # prime kernel for first model
    K.get_opview(app, A, "read")

    class B(Base):
        __tablename__ = "kernel_on_demand_b"
        __allow_unmapped__ = True
        id = acol(
            storage=S(type_=IntType, primary_key=True), io=IO(out_verbs=("read",))
        )

    bind(B)
    app.include_model(B, mount_router=False)

    # should compile opview without raising
    ov = K.get_opview(app, B, "read")
    assert ov is not None

    # cleanup
    K._opviews.pop(app, None)
    K._kernelz_payload.pop(app, None)
    K._primed.pop(app, None)
