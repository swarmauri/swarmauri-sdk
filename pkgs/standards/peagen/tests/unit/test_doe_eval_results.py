import json

import pytest

from peagen.core.doe_core import generate_payload
import peagen.core.doe_core as doe_core


@pytest.mark.unit
def test_generate_payload_writes_eval_results(tmp_path, monkeypatch):
    spec = {
        "version": "v2",
        "meta": {"name": "t"},
        "baseArtifact": "base.yaml",
        "factors": [
            {
                "name": "opt",
                "levels": [
                    {
                        "id": "adam",
                        "patchRef": "p1.yaml",
                        "output_path": "artifact.yaml",
                        "patchKind": "json-merge",
                    }
                ],
            }
        ],
    }
    base = tmp_path / "base.yaml"
    base.write_text("a: 1\n", encoding="utf-8")
    (tmp_path / "p1.yaml").write_text("b: 2\n", encoding="utf-8")
    spec_path = tmp_path / "spec.yaml"
    spec_path.write_text(json.dumps(spec))
    template_path = tmp_path / "template.yaml"
    template_path.write_text("PROJECTS: [{}]\n")
    output = tmp_path / "out.yaml"

    called = {}

    def fake_eval(**kwargs):
        called["repo"] = kwargs["repo"]
        return {"ok": True}

    monkeypatch.setattr(doe_core, "evaluate_workspace", fake_eval)

    generate_payload(
        spec_path=spec_path,
        template_path=template_path,
        output_path=output,
        skip_validate=True,
        evaluate_runs=True,
    )

    out_file = tmp_path / ".peagen" / "eval_results.json"
    assert out_file.exists()
    data = json.loads(out_file.read_text())
    assert data["ok"] is True
    assert called["repo"] == str(tmp_path)
