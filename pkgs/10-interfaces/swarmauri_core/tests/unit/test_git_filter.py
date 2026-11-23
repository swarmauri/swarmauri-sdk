import pytest

from swarmauri_core.git_filters import IGitFilter


def test_igitfilter_is_abstract():
    with pytest.raises(TypeError):
        IGitFilter()  # type: ignore[abstract]
