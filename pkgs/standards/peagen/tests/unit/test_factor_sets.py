import yaml
from pathlib import Path

from peagen.core.doe_core import _matrix_factor_sets, generate_payload


def test_matrix_factor_sets():
    fs = [
        {
            "name": "s1",
            "cartesianProduct": {"a": ["x", "y"], "b": ["1"]},
            "uriTemplate": "{a}-{b}",
        }
    ]
    points = _matrix_factor_sets(fs)
    assert points == [{"a": "x", "b": "1"}, {"a": "y", "b": "1"}]


def test_generate_payload_factor_sets(tmp_path: Path):
    patch = tmp_path / "p.yaml"
    patch.write_text("{}\n")
    spec = {
        "version": "v2",
        "meta": {"name": "t"},
        "factors": [
            {
                "name": "opt",
                "levels": [
                    {
                        "id": "adam",
                        "patchRef": patch.name,
                        "output_path": "art",
                        "patchKind": "json-merge",
                    },
                    {
                        "id": "sgd",
                        "patchRef": patch.name,
                        "output_path": "art",
                        "patchKind": "json-merge",
                    },
                ],
            },
            {
                "name": "lr",
                "levels": [
                    {
                        "id": "small",
                        "patchRef": patch.name,
                        "output_path": "art",
                        "patchKind": "json-merge",
                    },
                    {
                        "id": "big",
                        "patchRef": patch.name,
                        "output_path": "art",
                        "patchKind": "json-merge",
                    },
                ],
            },
        ],
        "factorSets": [
            {
                "name": "subset",
                "cartesianProduct": {"opt": ["adam"], "lr": ["small", "big"]},
                "uriTemplate": "{opt}-{lr}",
            }
        ],
    }
    spec_path = tmp_path / "spec.yaml"
    spec_path.write_text(yaml.safe_dump(spec))
    tmpl = Path(__file__).resolve().parents[2] / "docs/examples/base_example_project.yaml"
    out = tmp_path / "out.yaml"
    res = generate_payload(spec_path=spec_path, template_path=tmpl, output_path=out, dry_run=True, skip_validate=True)
    assert res["count"] == 2
