from __future__ import annotations

import asyncio
import re
from pathlib import Path

import pytest

README_PATH = Path(__file__).resolve().parents[2] / "README.md"


def _extract_quickstart_code() -> str:
    text = README_PATH.read_text(encoding="utf-8")
    match = re.search(r"```python\n(.*?)\n```", text, re.DOTALL)
    if not match:  # pragma: no cover - defensive, ensured by assert below
        raise AssertionError("README quickstart example not found")
    return match.group(1)


@pytest.mark.example
def test_readme_quickstart_executes() -> None:
    code = _extract_quickstart_code()
    namespace: dict[str, object] = {"__name__": "__README__"}
    exec(code, namespace)

    main = namespace.get("main")
    assert callable(main), "README quickstart must define main()"

    asyncio.run(main())  # type: ignore[arg-type]
