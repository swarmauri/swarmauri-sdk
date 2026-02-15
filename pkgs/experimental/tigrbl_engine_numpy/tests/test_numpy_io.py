from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from tigrbl_engine_numpy import numpy_engine


def test_numpy_session_save_and_load_npy(tmp_path: Path) -> None:
    target = tmp_path / "records.npy"
    _, session_factory = numpy_engine(
        mapping={
            "array": np.array([[1, "a"], [2, "b"]], dtype=object),
            "columns": ["id", "name"],
            "pk": "id",
        }
    )
    session = session_factory()

    session.save(str(target))
    loaded = session.load(str(target))

    assert target.exists()
    assert loaded.shape == (2, 2)
    assert loaded[0, 1] == "a"


def test_numpy_session_save_and_load_npz(tmp_path: Path) -> None:
    target = tmp_path / "records.npz"
    _, session_factory = numpy_engine(
        mapping={
            "array": np.array([[1, "a"]], dtype=object),
            "columns": ["id", "name"],
            "pk": "id",
        }
    )
    session = session_factory()

    session.save(str(target), npz_key="records")
    loaded = session.load(str(target), npz_key="records")

    assert target.exists()
    assert loaded.shape == (1, 2)
    assert loaded[0, 0] == 1


def test_numpy_session_memmap_modes(tmp_path: Path) -> None:
    path = tmp_path / "mapped.npy"
    _, session_factory = numpy_engine(
        mapping={
            "array": np.array([[0.0, 0.0]], dtype=float),
            "columns": ["id", "value"],
            "pk": "id",
        }
    )
    session = session_factory()

    mapped_w = session.memmap(str(path), mode="w+", dtype=np.float64, shape=(2, 2))
    mapped_w[:] = [[1.0, 2.0], [3.0, 4.0]]
    mapped_w.flush()

    mapped_r = session.memmap(str(path), mode="r", dtype=np.float64, shape=(2, 2))
    assert mapped_r[1, 1] == 4.0

    mapped_rp = session.memmap(str(path), mode="r+", dtype=np.float64, shape=(2, 2))
    mapped_rp[0, 0] = 9.0
    mapped_rp.flush()

    mapped_c = session.memmap(str(path), mode="c", dtype=np.float64, shape=(2, 2))
    mapped_c[0, 1] = 99.0

    mapped_verify = session.memmap(str(path), mode="r", dtype=np.float64, shape=(2, 2))
    assert mapped_verify[0, 0] == 9.0
    assert mapped_verify[0, 1] == 2.0


def test_numpy_session_memmap_rejects_invalid_mode(tmp_path: Path) -> None:
    path = tmp_path / "mapped.npy"
    _, session_factory = numpy_engine(
        mapping={"array": np.array([[1.0]]), "columns": ["id"], "pk": "id"}
    )
    session = session_factory()

    with pytest.raises(ValueError):
        session.memmap(str(path), mode="invalid")


def test_numpy_session_save_uses_atomic_replace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "atomic.npy"
    _, session_factory = numpy_engine(
        mapping={
            "array": np.array([[1, 2]], dtype=object),
            "columns": ["id", "v"],
            "pk": "id",
        }
    )
    session = session_factory()

    calls: list[tuple[str, str]] = []
    real_replace = __import__("os").replace

    def capture_replace(src: str, dst: str) -> None:
        calls.append((src, dst))
        real_replace(src, dst)

    monkeypatch.setattr("tigrbl_engine_numpy.session.os.replace", capture_replace)

    session.save(str(target))

    assert target.exists()
    assert len(calls) == 1
    assert calls[0][1] == str(target)
    assert Path(calls[0][0]).name.startswith(".tmp_")
