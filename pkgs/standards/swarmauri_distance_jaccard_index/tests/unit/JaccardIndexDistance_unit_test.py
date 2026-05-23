import warnings

import pytest

from swarmauri_distance_jaccard_index.JaccardIndexDistance import JaccardIndexDistance


@pytest.mark.unit
def test_import_emits_deprecation_warning():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        JaccardIndexDistance()
    assert any(item.category is DeprecationWarning for item in caught)
