import pytest
import pytest_asyncio
from autoapi.v3 import AutoAPI, Base, get_schema
from autoapi.v3.mixins import GUIDPk
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Column, String, create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from pydantic import Field


@pytest_asyncio.fixture()
async def api_client_with_extras(db_mode):
    Base.metadata.clear()

    class Widget(Base, GUIDPk):
        __tablename__ = "widgets"
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

        api = AutoAPI(base=Base, include={Widget}, get_async_db=get_async_db)
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

        api = AutoAPI(base=Base, include={Widget}, get_db=get_sync_db)
        api.initialize_sync()

    app = FastAPI()
    app.include_router(api.router)
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    return client, api, Widget


@pytest.mark.r8n
@pytest.mark.asyncio
async def test_request_extras_schema(api_client_with_extras):
    _, _, Widget = api_client_with_extras
    create_schema = get_schema(Widget, "create")
    update_schema = get_schema(Widget, "update")
    assert {"token", "create_note"} <= set(create_schema.model_fields)
    assert {"token", "update_flag"} <= set(update_schema.model_fields)


@pytest.mark.r8n
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
