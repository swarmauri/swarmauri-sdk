"""Demo ASGI app exposing OpenRPC JSON and a mounted tigrbl-lens UI."""

from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.system import mount_lens, mount_openrpc
from tigrbl.types import Column, String


class Widget(Base, GUIDPk):
    """Sample model used to generate JSON-RPC methods for lens demos."""

    __tablename__ = "widgets_lens_demo"
    name = Column(String, nullable=False)


app = TigrblApp(title="Tigrbl Lens Demo", version="0.1.0", engine=mem(async_=False))
app.include_model(Widget)
app.initialize()
app.mount_jsonrpc(prefix="/rpc")

mount_openrpc(app, app, path="/openrpc.json")
mount_lens(app, path="/lens", spec_path="/openrpc.json")
