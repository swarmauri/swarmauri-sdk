"""Expose the repository ``tests`` tree under ``tigrbl_tests.tests``."""

from pathlib import Path
from pkgutil import extend_path

# Preserve any existing namespace contributors for ``tigrbl_tests.tests``.
__path__ = extend_path(__path__, __name__)

# Add the in-repo tests directory so imports like
# ``tigrbl_tests.tests.i9n.uvicorn_utils`` resolve under isolated package runs.
_repo_tests = Path(__file__).resolve().parents[2] / "tests"
_repo_tests_str = str(_repo_tests)
if _repo_tests_str not in __path__:
    __path__.append(_repo_tests_str)
