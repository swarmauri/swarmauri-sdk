from tigrbl import TableBase
from pydantic import BaseModel
from tigrbl.shortcuts.app import deriveApp
from tigrbl.shortcuts.router import deriveRouter
from tigrbl.shortcuts.table import defineTableSpec
from tigrbl.orm.mixins import GUIDPk
from sqlalchemy import Column, String
from uuid import uuid4


class ExSchema(BaseModel):
    name: str


AppCls = deriveApp(schemas=[ExSchema])
ApiCls = deriveRouter(schemas=[ExSchema])


def test_app_houses_schemas():
    assert ExSchema in AppCls.SCHEMAS


def test_router_houses_schemas():
    assert ExSchema in ApiCls.SCHEMAS


def test_table_houses_schemas():
    TableBase.metadata.clear()

    Spec = defineTableSpec(schemas=[ExSchema])

    class Model(Spec, TableBase, GUIDPk):
        __tablename__ = f"schema_spec_model_{uuid4().hex}"
        name = Column(String)

    assert ExSchema in Model.SCHEMAS
