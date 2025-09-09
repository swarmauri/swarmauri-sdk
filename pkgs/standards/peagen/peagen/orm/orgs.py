from __future__ import annotations

from tigrbl.v3.orm.tables import Org as OrgBase


class Org(OrgBase):
    # __mapper_args__ = {"concrete": True}
    __table_args__ = (
        {
            "extend_existing": True,
            "schema": "peagen",
        },
    )


__all__ = ["Org"]
