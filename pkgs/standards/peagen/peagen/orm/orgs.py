from __future__ import annotations

from autoapi.v2.tables import Org as OrgBase

class Org(OrgBase):
    # __mapper_args__ = {"concrete": True}
    __table_args__ = ({
        "extend_existing": True,
        "schema": "peagen",
    },)


__all__ = ["Org"]
