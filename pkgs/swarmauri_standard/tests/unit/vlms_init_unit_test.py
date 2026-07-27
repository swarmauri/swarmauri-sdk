import subprocess
import sys

import pytest


@pytest.mark.unit
def test_vlm_namespace_does_not_eagerly_import_provider_packages():
    code = (
        "import sys; import swarmauri_standard.vlms; "
        "assert not any(name.startswith('swarmauri_llm_') "
        "for name in sys.modules)"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.unit
def test_vlm_submodule_imports_only_requested_provider():
    code = (
        "import sys, types; "
        "provider = types.ModuleType('swarmauri_llm_openai'); "
        "provider.OpenAIVLM = type('OpenAIVLM', (), {}); "
        "sys.modules['swarmauri_llm_openai'] = provider; "
        "from swarmauri_standard.vlms.OpenAIVLM import OpenAIVLM; "
        "assert OpenAIVLM.__name__ == 'OpenAIVLM'"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
