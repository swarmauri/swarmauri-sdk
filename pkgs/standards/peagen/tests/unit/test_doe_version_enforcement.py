import pytest
from pathlib import Path

from peagen.core.doe_core import generate_payload


@pytest.mark.unit
def test_generate_payload_rejects_legacy_spec(tmp_path: Path):
    root = Path(__file__).resolve().parents[2]
    spec = root / "tests/examples/doe_specs/doe_spec.yaml"
    template = root / "docs/examples/base_example_project.yaml"
    output = tmp_path / "out.yaml"
    with pytest.raises(ValueError, match="legacy DOE specs"):
        generate_payload(
            spec_path=spec,
            template_path=template,
            output_path=output,
            dry_run=True,
            skip_validate=True,
        )


@pytest.mark.unit
def test_generate_payload_rejects_bad_version(tmp_path: Path):
    spec = tmp_path / "bad.yaml"
    spec.write_text("version: v1\nmeta:\n  name: bad\n")
    root = Path(__file__).resolve().parents[2]
    template = root / "docs/examples/base_example_project.yaml"
    output = tmp_path / "out.yaml"
    with pytest.raises(ValueError, match="unsupported DOE spec version"):
        generate_payload(
            spec_path=spec,
            template_path=template,
            output_path=output,
            dry_run=True,
            skip_validate=True,
        )
