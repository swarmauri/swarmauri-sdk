# utils.py
from enum import Enum
from typing import List
import inflect

import peagen.orm as orm                       # ← import the *module*
import peagen.orm.schemas as orm_schemas       # ← import the *module*
from crouton import MemoryCRUDRouter, SQLAlchemyCRUDRouter  # type: ignore
from peagen.db.session import get_db


class RouterType(Enum):
    SQLALCHEMY = "sqlalchemy"
    MEMORY = "memory"


def create_route_objects(components: List[str]) -> List[dict]:
    p = inflect.engine()
    routes: List[dict] = []

    for component in components:
        # Skip umbrella / abstract symbols inadvertently listed in __all__
        if not hasattr(orm_schemas, component) or not hasattr(orm, f"{component}Model"):
            continue

        routes.append(
            {
                "schema":        getattr(orm_schemas, component),
                "create_schema": getattr(orm_schemas, component + "Create"),
                "update_schema": getattr(orm_schemas, component + "Update"),
                "db_model":      getattr(orm,        component + "Model"),
                "prefix":        p.plural(component.lower()),
            }
        )
    return routes


def create_routers(
    routes_to_create: List[dict],
    router_type: RouterType = RouterType.SQLALCHEMY,
) -> List:
    routers: List = []
    for route in routes_to_create:
        common = dict(
            schema=route["schema"],
            create_schema=route["create_schema"],
            update_schema=route["update_schema"],
            prefix=route["prefix"],
        )
        if router_type is RouterType.SQLALCHEMY:
            router = SQLAlchemyCRUDRouter(db_model=route["db_model"], db=get_db, **common)  # type: ignore[arg-type]
        else:
            router = MemoryCRUDRouter(**common)  # type: ignore[arg-type]
        routers.append(router)
    return routers
