from __future__ import annotations


_loaded = False


def load_engine_plugins() -> None:
    """Discover and load external engine plugins via entry points.
    Safe and idempotent; does nothing if already loaded.
    """
    global _loaded
    if _loaded:
        return

    # importlib.metadata API differs across Python versions; support both.
    eps = None
    try:
        from importlib.metadata import entry_points  # Python >= 3.10

        eps = entry_points()
        # New API: .select(group="tigrbl.engine")
        selected = (
            eps.select(group="tigrbl.engine")
            if hasattr(eps, "select")
            else eps.get("tigrbl.engine", [])
        )
    except Exception:
        try:
            from importlib_metadata import entry_points as entry_points_backport

            eps = entry_points_backport()
            selected = (
                eps.select(group="tigrbl.engine")
                if hasattr(eps, "select")
                else eps.get("tigrbl.engine", [])
            )
        except Exception:
            selected = []

    for ep in selected or []:
        try:
            fn = ep.load()
        except Exception:
            # Ignore broken entry points; the engine remains unavailable.
            continue
        try:
            fn()  # call plugin's register() to register_engine(kind, build, ...)
        except Exception:
            # Defensive: a broken plugin must not crash core import
            continue

    _loaded = True
