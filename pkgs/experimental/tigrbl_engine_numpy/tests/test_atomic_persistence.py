from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from tigrbl_engine_numpy import numpy_engine


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[int]


@pytest.mark.asyncio
async def test_numpy_session_commit_atomically_saves_npy(tmp_path: Path) -> None:
    path = tmp_path / "items.npy"
    np.save(path, np.array([[1, 10]], dtype=np.int64))

    _, make_session = numpy_engine(
        mapping={
            "path": str(path),
            "table": "items",
            "pk": "id",
            "columns": ["id", "value"],
        }
    )
    session = make_session()

    await session.begin()
    session.add(Item(id=2, value=20))
    await session.commit()

    loaded = np.load(path, allow_pickle=False)
    assert sorted(loaded.tolist()) == [[1, 10], [2, 20]]
