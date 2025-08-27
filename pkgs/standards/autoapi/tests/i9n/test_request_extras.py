import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import Field
from sqlalchemy import Column, String, create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from uuid import uuid4

from autoapi.v3 import AutoAPI, Base
from autoapi.v3.schema import _build_schema


@pytest_asyncio.fixture()
async def api_client_with_extras(db_mode):
    Base.metadata.clear()

    class Widget(Base):
        __tablename__ = "widgets"
        id = Column(String, primary_key=True, default=lambda: str(uuid4()))
        name = Column(String, nullable=False)
        __autoapi_request_extras__ = {
            "*": {"token": (str | None, Field(default=None, exclude=True))},
            "create": {"create_note": (str | None, Field(default=None, exclude=True))},
            "update": {"update_flag": (bool | None, Field(default=None, exclude=True))},
        }

    if db_mode == "async":
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        AsyncSessionLocal = async_sessionmaker(
            bind=engine, class_=AsyncSession, expire_on_commit=False
        )

        async def get_async_db() -> AsyncSession:
            async with AsyncSessionLocal() as session:
                yield session

        api = AutoAPI(get_async_db=get_async_db)
        api.include_model(Widget)
        await api.initialize_async()
    else:
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

        def get_sync_db() -> Session:
            with SessionLocal() as session:
                yield session

        api = AutoAPI(get_db=get_sync_db)
        api.include_model(Widget)
        api.initialize_sync()

    app = FastAPI()
    app.include_router(api.router)
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    return client, api, Widget


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_request_extras_schema(api_client_with_extras):
    _, _, Widget = api_client_with_extras
    create_schema = _build_schema(Widget, verb="create")
    update_schema = _build_schema(Widget, verb="update")
    assert {"token", "create_note"} <= set(create_schema.model_fields)
    assert {"token", "update_flag"} <= set(update_schema.model_fields)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_request_extras_runtime(api_client_with_extras):
    client, _, _ = api_client_with_extras
    res = await client.post(
        "/widget",
        json={"name": "w1", "token": "t", "create_note": "note"},
    )
    assert res.status_code == 201
    body = res.json()
    wid = body["id"]
    assert "token" not in body and "create_note" not in body

    res = await client.patch(
        f"/widget/{wid}",
        json={"name": "w2", "token": "t2", "update_flag": True},
    )
    assert res.status_code == 200

    body = res.json()
    assert "token" not in body and "update_flag" not in body
