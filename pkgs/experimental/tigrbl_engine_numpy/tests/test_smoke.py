from pathlib import Path

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
    assert len(session.to_records()) == 2


def test_numpy_engine_supports_npy_npz_load_and_memmap_modes(tmp_path: Path) -> None:
    npy_path = tmp_path / "records.npy"
    npz_path = tmp_path / "records.npz"
    memmap_path = tmp_path / "records.dat"

    base = np.array([[1, 10], [2, 20]], dtype=np.int64)
    np.save(npy_path, base)
    np.savez(npz_path, records=base)

    mm = np.memmap(memmap_path, dtype="int64", mode="w+", shape=(2, 2))
    mm[:] = base
    mm.flush()
    del mm

    loaded_npy, _ = numpy_engine(
        mapping={"path": str(npy_path), "table": "records", "columns": ["id", "value"]}
    )
    assert loaded_npy.array.tolist() == [[1, 10], [2, 20]]

    loaded_npz, _ = numpy_engine(
        mapping={
            "path": str(npz_path),
            "npz_key": "records",
            "table": "records",
            "columns": ["id", "value"],
        }
    )
    assert loaded_npz.array.tolist() == [[1, 10], [2, 20]]

    mode_to_expected = {
        "r": [[1, 10], [2, 20]],
        "r+": [[1, 10], [2, 20]],
        "w+": [[0, 0], [0, 0]],
        "c": [[1, 10], [2, 20]],
    }
    for mode, expected in mode_to_expected.items():
        current_path = memmap_path
        mm_mode = np.memmap(current_path, dtype="int64", mode="w+", shape=(2, 2))
        mm_mode[:] = base
        mm_mode.flush()
        del mm_mode

        engine, _ = numpy_engine(
            mapping={
                "path": str(current_path),
                "use_memmap": True,
                "mode": mode,
                "dtype": "int64",
                "shape": (2, 2),
                "table": "records",
                "columns": ["id", "value"],
            }
        )
        assert engine.array.tolist() == expected
