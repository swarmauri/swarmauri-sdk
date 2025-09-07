import asyncio
import io
import logging

import httpx
import pytest
import pytest_asyncio
import uvicorn

from autoapi.v3 import AutoApp
from autoapi.v3.orm.tables._base import Base
from autoapi.v3.specs import F, IO, S, acol
from autoapi.v3.types import App, Mapped, String


class Token(Base):
    __abstract__ = False
    __tablename__ = "tokens_uvicorn"
    __resource__ = "token"

    value: Mapped[str] = acol(
        storage=S(String, primary_key=True, nullable=False),
        field=F(py_type=str, paired=True),
        io=IO(in_verbs=("create",), out_verbs=("read",)),
    )


@pytest_asyncio.fixture()
async def running_app(sync_db_session):
    engine, get_sync_db = sync_db_session

    app = App()
    api = AutoApp(get_db=get_sync_db)
    api.include_models([Token])
    api.initialize()
    app.include_router(api.router)

    cfg = uvicorn.Config(app, host="127.0.0.1", port=8001, log_level="debug")
    server = uvicorn.Server(cfg)

    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    logger = logging.getLogger("uvicorn")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    task = asyncio.create_task(server.serve())
    while not server.started:
        await asyncio.sleep(0.1)
    try:
        yield ("http://127.0.0.1:8001", log_stream)
    finally:
        server.should_exit = True
        await task
        logger.removeHandler(handler)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_resolve_paired_gen_logged(running_app):
    base_url, log_stream = running_app
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{base_url}/token", json={})
    assert resp.status_code == 201
    assert "Running resolve:paired_gen" in log_stream.getvalue()
