# peagen/db/api/v1/utils.py
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


def create_route_objects(components: list[str]) -> list[dict]:
    p       = inflect.engine()
    routes: list[dict] = []

    for name in components:
        read     = f"{name}Read"
        create   = f"{name}Create"
        update   = f"{name}Update"

        # ensure all required schemas exist
        if not all(hasattr(orm_schemas, s) for s in (read, create, update)):
            continue

        routes.append(
            {
                "schema":        getattr(orm_schemas, read),
                "create_schema": getattr(orm_schemas, create),
                "update_schema": getattr(orm_schemas, update),
                "db_model":      getattr(orm, f"{name}Model"),
                "prefix":        p.plural(name.lower()),
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

def attach_list_of_routers(app, list_of_routers: List) -> None:
    """
    Attach a list of routers to the given FastAPI app.

    Args:
        app: FastAPI application instance.
        list_of_routers (List): List of routers to attach.
    """
    for router in list_of_routers:
        app.include_router(router)
