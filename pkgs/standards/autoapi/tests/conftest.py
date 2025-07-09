from contextlib import asynccontextmanager
from typing import AsyncIterator

import pytest_asyncio
from autoapi.v2 import AutoAPI, Base
from autoapi.v2.mixins import BulkCapable, GUIDPk
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


@pytest_asyncio.fixture()
async def api_client():
    class Tenant(Base, GUIDPk):
        __tablename__ = "tenants"
        name = Column(String, nullable=False)

    class Item(Base, GUIDPk, BulkCapable):
        __tablename__ = "items"
        tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
        name = Column(String, nullable=False)
        _nested_path = "/tenants/{tenant_id}"

    @asynccontextmanager
    async def get_db() -> AsyncIterator[AsyncSession]:
        async_engine = create_async_engine("sqlite+aiosqlite:///gateway.db", echo=True)
        async_session_factory = async_sessionmaker(
            bind=async_engine, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session_factory() as session:
            try:
                yield session
            finally:
                await session.close()

    api = AutoAPI(
        base=Base, include={Tenant, Item}, get_async_db=get_db
    )  # Changed from get_db to get_async_db
    await api.initialize_async()

    app = FastAPI()
    app.include_router(api.router)
    transport = ASGITransport(app=app)

    client = AsyncClient(transport=transport, base_url="http://test")
    return client, api, Item
