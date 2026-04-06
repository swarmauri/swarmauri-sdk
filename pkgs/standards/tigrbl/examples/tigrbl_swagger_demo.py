"""Minimal Tigrbl app for Swagger UI demos.

Run with:
    uv run --package tigrbl --directory pkgs/standards/tigrbl \
      uvicorn examples.tigrbl_swagger_demo:app --host 127.0.0.1 --port 8010
Then open:
    http://127.0.0.1:8010/docs
Capture a headless screenshot:
    wkhtmltoimage --javascript-delay 2000 \
      http://127.0.0.1:8010/docs /tmp/tigrbl-swagger-ui.png
"""

from tigrbl import TableBase, TigrblApp
from tigrbl.orm.mixins import GUIDPk
from tigrbl.shortcuts.engine import mem
from tigrbl.types import Column, String


class Note(TableBase, GUIDPk):
    __tablename__ = "notes"
    __allow_unmapped__ = True

    title = Column(String, nullable=False)


app = TigrblApp(engine=mem(async_=False), title="Tigrbl Swagger Demo", version="0.1.0")
app.include_table(Note)
app.initialize()
