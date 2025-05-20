# peagen/utils.py
from contextlib import contextmanager
from pathlib import Path
import tempfile
import shutil
import logging

@contextmanager
def temp_workspace(prefix: str = "peagen_"):
    """Yield a temporary directory that is removed on exit."""
    dirpath = Path(tempfile.mkdtemp(prefix=prefix))
    try:
        yield dirpath          # ←  every path you write will be under here
    finally:
        try:
            shutil.rmtree(dirpath)
        except FileNotFoundError:
            # Already removed – fine.
            pass
        except OSError as exc:
            logging.warning(f"Workspace cleanup failed: {exc}")
