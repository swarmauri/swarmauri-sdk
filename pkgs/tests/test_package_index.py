from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_INDEX_SCRIPT = REPO_ROOT / "scripts" / "package_index.py"


def _load_package_index_module():
    spec = importlib.util.spec_from_file_location("package_index", PACKAGE_INDEX_SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_package_index_is_valid_and_markdown_is_current():
    package_index = _load_package_index_module()

    errors = package_index.validate_index(check_docs=True)

    assert errors == []
