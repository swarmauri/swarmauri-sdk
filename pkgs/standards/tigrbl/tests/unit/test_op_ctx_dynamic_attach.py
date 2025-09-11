from tigrbl import TigrblApi, Base, op_ctx
from sqlalchemy.orm import Mapped, mapped_column


def test_op_ctx_dynamic_attach_auto_discovers_ops():
    api = TigrblApi()

    class Book(Base):
        __tablename__ = "book"
        id: Mapped[int] = mapped_column(primary_key=True)

    api.include_model(Book, mount_router=False)
    assert "publish" not in [sp.alias for sp in Book.ops.all]

    @op_ctx(bind=Book)
    def publish(cls, ctx):
        return None

    assert "publish" in [sp.alias for sp in Book.ops.all]
