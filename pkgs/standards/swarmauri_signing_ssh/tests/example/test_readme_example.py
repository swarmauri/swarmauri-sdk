from __future__ import annotations

from pathlib import Path
import textwrap
from typing import Awaitable, Callable, cast

import pytest


README_PATH = Path(__file__).resolve().parents[2] / "README.md"
_BLOCK_HEADER = '```python title="README example: sign and verify an SSH signature"'


def _extract_readme_example() -> str:
    content = README_PATH.read_text(encoding="utf-8")
    in_block = False
    lines: list[str] = []
    for line in content.splitlines():
        if not in_block and line.strip() == _BLOCK_HEADER:
            in_block = True
            continue
        if in_block:
            if line.strip().startswith("```"):
                break
            lines.append(line)
    if not lines:
        raise AssertionError("README example block was not found")
    return textwrap.dedent("\n".join(lines))


@pytest.mark.asyncio
@pytest.mark.example
async def test_readme_example_executes() -> None:
    code = _extract_readme_example()
    module_globals: dict[str, object] = {"__name__": "__readme__"}
    exec(compile(code, str(README_PATH), "exec"), module_globals)  # noqa: S102
    main_obj = module_globals.get("main")
    assert callable(main_obj), "README example must define a callable 'main'"
    main = cast(Callable[[], Awaitable[bool]], main_obj)

    result = await main()
    assert result is True
