"""Legacy imports remain, but the decommissioned audio API is disabled."""

import pytest
from swarmauri_llm_hyperbolic import HyperbolicAudioTTS

pytestmark = pytest.mark.unit


def test_legacy_type_metadata_is_retained():
    assert (
        HyperbolicAudioTTS.model_fields["type"].default == "HyperbolicAudioTTS"
    )
    assert HyperbolicAudioTTS.model_fields["resource"].default == "LLM"
    with pytest.warns(FutureWarning, match="decommissioned"):
        with pytest.raises(RuntimeError, match="decommissioned"):
            HyperbolicAudioTTS(api_key="old-key")
