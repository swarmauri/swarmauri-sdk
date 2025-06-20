import json
from pathlib import Path

import pytest

from peagen.core.doe_core import generate_payload


@pytest.mark.unit
def test_factor_sets_expand_design_points(tmp_path: Path) -> None:
    spec = {
        "version": "v2",
        "meta": {"name": "t"},
        "baseArtifact": "base.yaml",
        "factors": [
            {
                "name": "dataset",
                "levels": [
                    {
                        "id": "news",
                        "patchRef": "p.yaml",
                        "output_path": "artifact.yaml",
                    }
                ],
            },
            {
                "name": "provider",
                "levels": [
                    {
                        "id": "openai",
                        "patchRef": "p.yaml",
                        "output_path": "artifact.yaml",
                    },
                    {
                        "id": "groq",
                        "patchRef": "p.yaml",
                        "output_path": "artifact.yaml",
                    },
                ],
            },
            {
                "name": "temperature",
                "levels": [
                    {
                        "id": "0.2",
                        "patchRef": "p.yaml",
                        "output_path": "artifact.yaml",
                    },
                    {
                        "id": "0.7",
                        "patchRef": "p.yaml",
                        "output_path": "artifact.yaml",
                    },
                ],
            },
        ],
        "factorSets": [
            {
                "name": "llm",
                "cartesianProduct": {
                    "provider": ["openai", "groq"],
                    "temperature": ["0.2", "0.7"],
                },
                "uriTemplate": "x",
            }
        ],
    }

    (tmp_path / "base.yaml").write_text("a: 1\n", encoding="utf-8")
    (tmp_path / "p.yaml").write_text("- op: add\n  path: /b\n  value: 2\n", encoding="utf-8")

    spec_path = tmp_path / "spec.yaml"
    spec_path.write_text(json.dumps(spec))
    template = tmp_path / "t.yaml"
    template.write_text("PROJECTS:\n  - {}\n")
    out = tmp_path / "out.yaml"

    result = generate_payload(
        spec_path=spec_path,
        template_path=template,
        output_path=out,
        skip_validate=True,
    )

    assert result["count"] == 4
    assert set(result["llm_keys"]) == {"provider", "temperature"}
    assert result["other_keys"] == ["dataset"]
