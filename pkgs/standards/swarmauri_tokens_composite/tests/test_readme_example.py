import re
from pathlib import Path
from typing import Any, Dict

import pytest


README_PATH = Path(__file__).resolve().parents[1] / "README.md"
EXAMPLE_MARKER = "# README Example: CompositeTokenService basic routing"


@pytest.mark.example
def test_readme_example_executes() -> None:
    readme_text = README_PATH.read_text(encoding="utf-8")
    pattern = re.compile(
        r"```python\n(?P<code>.*?" + re.escape(EXAMPLE_MARKER) + r".*?)\n```",
        re.DOTALL,
    )
    match = pattern.search(readme_text)
    assert match, "Could not locate the CompositeTokenService example in README.md"

    code = match.group("code")
    namespace: Dict[str, Any] = {}
    exec(code, namespace)

    assert "example_result" in namespace, "Example did not populate 'example_result'"
    result = namespace["example_result"]

    assert result["jwt_token"] == "JWTTokenService:HS256:alice"
    assert result["ssh_token"] == "SshCertTokenService:ssh-ed25519:bob"
    assert result["jwt_claims"]["service"] == "JWTTokenService"
    assert result["ssh_claims"]["service"] == "SshCertTokenService"

    kids = {entry["kid"] for entry in result["jwks"]["keys"]}
    assert kids == {"JWTTokenService-kid", "SshCertTokenService-kid"}
