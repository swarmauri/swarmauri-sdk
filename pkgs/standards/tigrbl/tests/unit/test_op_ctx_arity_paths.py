from tigrbl.types import App
from tigrbl import op_ctx
from tigrbl.op.mro_collect import mro_collect_decorated_ops
from tigrbl.bindings.rest.router import _build_router
from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_member_arity_rest_path_includes_pk():
    Base.metadata.clear()

    class MemberModel(Base, GUIDPk):
        __tablename__ = "member_path_model"
        name = Column(String, nullable=False)

        @op_ctx(alias="do", arity="member")
        def do(cls, ctx):
            return None

    spec = mro_collect_decorated_ops(MemberModel)[0]
    router = _build_router(MemberModel, [spec])
    paths = {route.path for route in router.routes}
    assert f"/{MemberModel.__name__.lower()}/{{item_id}}/do" in paths


def test_collection_arity_rest_path_excludes_pk():
    Base.metadata.clear()

    class CollectionModel(Base, GUIDPk):
        __tablename__ = "collection_path_model"
        name = Column(String, nullable=False)

        @op_ctx(alias="do", arity="collection")
        def do(cls, ctx):
            return None

    spec = mro_collect_decorated_ops(CollectionModel)[0]
    router = _build_router(CollectionModel, [spec])
    paths = {route.path for route in router.routes}
    assert f"/{CollectionModel.__name__.lower()}/do" in paths


def test_member_arity_openapi_has_path_param():
    Base.metadata.clear()

    class MemberModel(Base, GUIDPk):
        __tablename__ = "member_openapi_model"
        name = Column(String, nullable=False)

        @op_ctx(alias="do", arity="member")
        def do(cls, ctx):
            return None

    spec = mro_collect_decorated_ops(MemberModel)[0]
    router = _build_router(MemberModel, [spec])
    app = App()
    app.include_router(router)
    params = app.openapi()["paths"][f"/{MemberModel.__name__.lower()}/{{item_id}}/do"][
        "post"
    ]["parameters"]
    assert any(p["name"] == "item_id" for p in params)


def test_collection_arity_openapi_has_no_path_param():
    Base.metadata.clear()

    class CollectionModel(Base, GUIDPk):
        __tablename__ = "collection_openapi_model"
        name = Column(String, nullable=False)

        @op_ctx(alias="do", arity="collection")
        def do(cls, ctx):
            return None

    spec = mro_collect_decorated_ops(CollectionModel)[0]
    router = _build_router(CollectionModel, [spec])
    app = App()
    app.include_router(router)
    operation = app.openapi()["paths"][f"/{CollectionModel.__name__.lower()}/do"][
        "post"
    ]
    assert "parameters" not in operation
