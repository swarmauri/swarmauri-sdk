import os

class EnvSecret:
    """Simple secret provider that reads values from environment variables."""

    def __init__(self, prefix: str | None = None) -> None:
        self.prefix = prefix or ""

    def get(self, name: str) -> str:
        var = f"{self.prefix}{name}"
        val = os.getenv(var)
        if val is None:
            raise KeyError(f"Environment variable {var} not set")
        return val
