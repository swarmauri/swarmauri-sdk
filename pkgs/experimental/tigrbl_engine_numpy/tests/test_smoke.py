import numpy as np

from tigrbl_engine_numpy import numpy_engine


def test_numpy_engine_smoke() -> None:
    engine, session_factory = numpy_engine(
        mapping={
            "array": np.array([[1, 3], [2, 5]]),
            "table": "items",
            "columns": ["id", "value"],
            "pk": "id",
        }
    )
    session = session_factory()
    assert engine.array.shape == (2, 2)
    assert session.array().shape == (2, 2)
