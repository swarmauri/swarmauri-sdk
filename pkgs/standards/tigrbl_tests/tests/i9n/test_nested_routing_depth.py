import pytest
import pytest_asyncio
from tigrbl import TigrblApp, Base
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import App
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Column, ForeignKey, String
from tigrbl.types import PgUUID


@pytest_asyncio.fixture
async def three_level_api_client(db_mode):
    Base.metadata.clear()
    Base.registry.dispose()

    class Company(Base, GUIDPk):
        __tablename__ = "companies"
        name = Column(String, nullable=False)

    class Department(Base, GUIDPk):
        __tablename__ = "departments"
        company_id = Column(
            PgUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False
        )
        name = Column(String, nullable=False)

        @classmethod
        def __tigrbl_nested_paths__(cls):
            return "/company/{company_id}/department"

    class Employee(Base, GUIDPk):
        __tablename__ = "employees"
        company_id = Column(
            PgUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False
        )
        department_id = Column(
            PgUUID(as_uuid=True), ForeignKey("departments.id"), nullable=False
        )
        name = Column(String, nullable=False)

        @classmethod
        def __tigrbl_nested_paths__(cls):
            return "/company/{company_id}/department/{department_id}/employee"

    if db_mode == "async":
        pytest.skip("async database mode is currently unsupported")
    else:
        api = TigrblApp(engine=mem(async_=False))
        api.include_models([Company, Department, Employee])
        api.initialize()

    app = App()
    app.include_router(api.router)
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    return client


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_nested_routing_depth(three_level_api_client):
    client = three_level_api_client

    # Create company
    res = await client.post("/company", json={"name": "Acme"})
    assert res.status_code == 201
    company_id = res.json()["id"]

    # Create department
    res = await client.post(
        f"/company/{company_id}/department",
        json={"name": "Engineering"},
    )
    assert res.status_code == 201
    department_id = res.json()["id"]

    # Create employee
    res = await client.post(
        f"/company/{company_id}/department/{department_id}/employee",
        json={"name": "Alice"},
    )
    assert res.status_code == 201
    employee_id = res.json()["id"]

    # Verify generated REST paths and HTTP methods
    paths = (await client.get("/openapi.json")).json()["paths"]
    expected = {
        "/company": {"post", "get", "delete"},
        "/company/{item_id}": {"get", "patch", "delete"},
        "/company/{company_id}/department": {"post", "get", "delete"},
        "/company/{company_id}/department/{item_id}": {"get", "patch", "delete"},
        "/company/{company_id}/department/{department_id}/employee": {
            "post",
            "get",
            "delete",
        },
        "/company/{company_id}/department/{department_id}/employee/{item_id}": {
            "get",
            "patch",
            "delete",
        },
    }
    for path, verbs in expected.items():
        assert path in paths
        for verb in verbs:
            assert verb in paths[path]

    # Confirm nested routes resolve to correct handlers
    res = await client.get(f"/company/{company_id}/department/{department_id}")
    assert res.status_code == 200
    assert res.json()["id"] == department_id

    res = await client.get(
        f"/company/{company_id}/department/{department_id}/employee/{employee_id}"
    )
    assert res.status_code == 200
    assert res.json()["id"] == employee_id
