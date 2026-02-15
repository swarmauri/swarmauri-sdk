"""tigrbl_engine_pandas: DataFrame-backed Tigrbl engine"""

from .engine import pandas_engine, pandas_capabilities, DataFrameCatalog
from .session import TransactionalDataFrameSession

__all__ = [
    "pandas_engine",
    "pandas_capabilities",
    "DataFrameCatalog",
    "TransactionalDataFrameSession",
    "register",
]


def register() -> None:
    """
    Entry point target for group 'tigrbl.engine'. This function will be loaded
    by Tigrbl's plugin system. It attempts to register the 'pandas' kind
    with whatever registry is exposed by the installed Tigrbl version.
    """
    register_fn = None
    try:
        from tigrbl.engine.registry import register_engine as _reg

        register_fn = _reg
    except Exception:
        try:
            from tigrbl.engine.plugins import register_engine as _reg2

            register_fn = _reg2
        except Exception:
            try:
                from tigrbl.engine import register_engine as _reg3  # type: ignore

                register_fn = _reg3
            except Exception as exc:
                raise RuntimeError(
                    "Could not locate Tigrbl engine registry to register plugin"
                ) from exc

    register_fn("pandas", pandas_engine, pandas_capabilities)
