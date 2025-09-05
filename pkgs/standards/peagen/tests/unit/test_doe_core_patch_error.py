import pytest
from pathlib import Path

from peagen.core.doe_core import generate_payload


@pytest.mark.unit
def test_generate_payload_missing_patch(tmp_path: Path):
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
