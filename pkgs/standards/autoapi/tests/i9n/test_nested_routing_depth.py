import pytest
import pytest_asyncio
from autoapi.v3 import AutoAPI, Base
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.types import App
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Column, ForeignKey, String


@pytest_asyncio.fixture
async def three_level_api_client(db_mode, sync_db_session, async_db_session):
    Base.metadata.clear()

    class Company(Base, GUIDPk):
        __tablename__ = "companies"
        name = Column(String, nullable=False)

    class Department(Base, GUIDPk):
        __tablename__ = "departments"
        company_id = Column(String, ForeignKey("companies.id"), nullable=False)
        name = Column(String, nullable=False)

        @classmethod
        def __autoapi_nested_paths__(cls):
            return "/company/{company_id}"

    class Employee(Base, GUIDPk):
        __tablename__ = "employees"
        company_id = Column(String, ForeignKey("companies.id"), nullable=False)
        department_id = Column(String, ForeignKey("departments.id"), nullable=False)
        name = Column(String, nullable=False)

        @classmethod
        def __autoapi_nested_paths__(cls):
            return "/company/{company_id}/department/{department_id}"

    if db_mode == "async":
        _, get_async_db = async_db_session
        api = AutoAPI(get_async_db=get_async_db)
        api.include_models([Company, Department, Employee])
        await api.initialize_async()
    else:
        _, get_sync_db = sync_db_session
        api = AutoAPI(get_db=get_sync_db)
        api.include_models([Company, Department, Employee])
        api.initialize_sync()

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
        f"/company/{company_id}",
        json={"name": "Engineering"},
    )
    assert res.status_code == 201
    department_id = res.json()["id"]

    # Create employee
    res = await client.post(
        f"/company/{company_id}/department/{department_id}",
        json={"name": "Alice"},
    )
    assert res.status_code == 201
    employee_id = res.json()["id"]

    # Verify generated REST paths and HTTP methods
    paths = (await client.get("/openapi.json")).json()["paths"]
    expected = {
        "/company": {"post", "get", "delete"},
        "/company/{item_id}": {"get", "patch", "delete"},
        "/company/{company_id}": {"post", "get", "delete"},
        "/company/{company_id}/{item_id}": {"get", "patch", "delete"},
        "/company/{company_id}/department/{department_id}": {
            "post",
            "get",
            "delete",
        },
        "/company/{company_id}/department/{department_id}/{item_id}": {
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
    res = await client.get(f"/company/{company_id}/{department_id}")
    assert res.status_code == 200
    assert res.json()["id"] == department_id

    res = await client.get(
        f"/company/{company_id}/department/{department_id}/{employee_id}"
    )
    assert res.status_code == 200
    assert res.json()["id"] == employee_id
