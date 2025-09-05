from pathlib import Path

import pytest

from peagen.plugins.evaluators.psutil_io import PsutilIOEvaluator


@pytest.mark.unit
def test_psutil_io_evaluator(tmp_path: Path):
    script = tmp_path / "writer.py"
    script.write_text("with open('out.bin','wb') as f: f.write(b'x'*1024)")
    evaluator = PsutilIOEvaluator()
    fitness = evaluator.run(tmp_path, f"python {script}")
    assert evaluator.last_result is not None
    assert evaluator.last_result["median_mib"] >= 0
    assert fitness <= 0
