"""Export JSON schema for all protocol models."""

from __future__ import annotations

import json
from pathlib import Path

from peagen.protocols import _registry


def main() -> None:
    out_dir = Path("build/jsonschema")
    out_dir.mkdir(parents=True, exist_ok=True)
    schema: dict[str, dict] = {}
    for method, spec in _registry._registry.items():  # type: ignore[attr-defined]
        schema[method] = {
            "params": spec.params.model_json_schema(),
            "result": spec.result.model_json_schema(),
        }
    (out_dir / "protocols.json").write_text(json.dumps(schema, indent=2))


if __name__ == "__main__":  # pragma: no cover
    main()
