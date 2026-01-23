from pydantic import BaseModel
from tigrbl.app.shortcuts import deriveApp
from tigrbl.api.shortcuts import deriveApi
from tigrbl.table.shortcuts import defineTableSpec
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import Base
from sqlalchemy import Column, String
from uuid import uuid4


class ExSchema(BaseModel):
    name: str


AppCls = deriveApp(schemas=[ExSchema])
ApiCls = deriveApi(schemas=[ExSchema])


def test_app_houses_schemas():
    assert ExSchema in AppCls.SCHEMAS


def test_api_houses_schemas():
    assert ExSchema in ApiCls.SCHEMAS


def test_table_houses_schemas():
    Base.metadata.clear()

    Spec = defineTableSpec(schemas=[ExSchema])

    class Model(Spec, Base, GUIDPk):
        __tablename__ = f"schema_spec_model_{uuid4().hex}"
        name = Column(String)

    assert ExSchema in Model.SCHEMAS
