from tigrbl import TigrblApp
from tigrbl.bindings.model import bind
from tigrbl.orm.tables import Base
from tigrbl.runtime.kernel import _default_kernel as K
from tigrbl.specs import IO, S, acol
from tigrbl.types import Integer as IntType


def test_kernel_get_opview_caches_runtime_result() -> None:
    Base.metadata.clear()

    class RuntimeKernelModel(Base):
        __tablename__ = "runtime_kernel_behavior"
        __allow_unmapped__ = True
        id = acol(
            storage=S(type_=IntType, primary_key=True), io=IO(out_verbs=("read",))
        )

    bind(RuntimeKernelModel)
    app = TigrblApp()
    app.include_model(RuntimeKernelModel, mount_router=False)

    first = K.get_opview(app, RuntimeKernelModel, "read")
    second = K.get_opview(app, RuntimeKernelModel, "read")

    assert first is second

    K._opviews.pop(app, None)
    K._kernelz_payload.pop(app, None)
    K._primed.pop(app, None)
