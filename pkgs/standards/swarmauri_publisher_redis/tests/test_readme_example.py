from __future__ import annotations

import json
import re
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.mark.example
def test_readme_quickstart(monkeypatch: pytest.MonkeyPatch) -> None:
    """Execute the README quickstart example to ensure it stays valid."""
    readme_path = Path(__file__).resolve().parents[1] / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8")

    code_blocks = re.findall(r"```python\n(.*?)\n```", readme_text, re.DOTALL)
    example_block = next(
        (block for block in code_blocks if "RedisPublisher" in block),
        None,
    )

    assert example_block is not None, (
        "Could not find the README RedisPublisher example."
    )

    published_messages: list[tuple[str, str]] = []

    def fake_from_url(*_args, **_kwargs) -> SimpleNamespace:
        def _publish(channel: str, payload: str) -> None:
            published_messages.append((channel, payload))

        return SimpleNamespace(publish=_publish)

    monkeypatch.setattr("redis.from_url", fake_from_url)

    namespace: dict[str, object] = {"__name__": "__main__"}
    exec(example_block, namespace)

    assert published_messages, "README example did not publish any messages."

    channel, payload = published_messages[0]
    assert isinstance(channel, str)
    assert isinstance(payload, str)
    assert json.loads(payload)["message"] == "Hello Redis!"
