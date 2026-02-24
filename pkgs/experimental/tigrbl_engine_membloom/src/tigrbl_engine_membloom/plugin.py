from __future__ import annotations

from tigrbl.engine.registry import register_engine

from .bloom import BloomFilter, BloomRing
from .session import AsyncBloomSession, BloomSession


def register() -> None:
    register_engine(
        kind="membloom",
        build=build_membloom,
        capabilities=capabilities,
    )


def capabilities() -> dict:
    return {
        "engine": "membloom",
        "transactional": False,
        "async_native": True,
        "persistence": "process",
        "features": {"bloom", "approx_membership", "ttl_optional"},
        "notes": (
            "Probabilistic set membership; false positives possible, "
            "false negatives are not expected unless keys have expired by TTL."
        ),
    }


def build_membloom(*, mapping=None, spec=None, dsn=None, **_) -> tuple[object, object]:
    mapping = dict(mapping or {})
    async_ = bool(getattr(spec, "async_", False))

    capacity = int(mapping.get("capacity", 1_000_000))
    fp_rate = float(mapping.get("fp_rate", 1e-4))
    seed = str(mapping.get("seed", "tigrbl:membloom:v1"))
    namespace = str(mapping.get("namespace", "default"))

    windows = int(mapping.get("windows", 1))
    window_seconds = float(mapping.get("window_seconds", 0.0)) or None

    if windows < 1:
        raise ValueError("windows must be >= 1")

    if windows == 1 or window_seconds is None:
        engine = BloomFilter.from_capacity(
            capacity=capacity,
            fp_rate=fp_rate,
            seed=f"{seed}:{namespace}",
        )
    else:
        engine = BloomRing.from_capacity(
            capacity=capacity,
            fp_rate=fp_rate,
            seed=f"{seed}:{namespace}",
            windows=windows,
            window_seconds=window_seconds,
        )

    if async_:

        def sessionmaker():
            return AsyncBloomSession(engine)
    else:

        def sessionmaker():
            return BloomSession(engine)

    return engine, sessionmaker
