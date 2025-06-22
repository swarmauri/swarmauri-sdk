from __future__ import annotations


class EchoMutator:
    """Trivial mutator used for testing."""

    def __init__(self, *_, **__):
        pass

    def mutate(self, prompt: str) -> str:
        """Return the original code extracted from *prompt* with a comment."""
        import re

        match = re.search(r"```python\n(.+?)```", prompt, re.DOTALL)
        src = match.group(1) if match else prompt
        return src + "\n# mutated\n"
