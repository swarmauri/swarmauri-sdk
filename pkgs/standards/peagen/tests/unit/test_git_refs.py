import pytest

from peagen.git import (
    PEAGEN_REFS_PREFIX,
    FACTOR_REF,
    RUN_REF,
    ANALYSIS_REF,
    EVO_REF,
    PROMOTED_REF,
    pea_ref,
)


@pytest.mark.unit
def test_constants():
    assert PEAGEN_REFS_PREFIX == "refs/pea"
    assert FACTOR_REF == "refs/pea/factor"
    assert RUN_REF == "refs/pea/run"
    assert ANALYSIS_REF == "refs/pea/analysis"
    assert EVO_REF == "refs/pea/evo"
    assert PROMOTED_REF == "refs/pea/promoted"


@pytest.mark.unit
@pytest.mark.parametrize(
    "parts,expected",
    [
        (("run", "abc"), "refs/pea/run/abc"),
        (("analysis", "res"), "refs/pea/analysis/res"),
    ],
)
def test_pea_ref(parts, expected):
    assert pea_ref(*parts) == expected

    with pytest.raises(ValueError):
        pea_ref()
