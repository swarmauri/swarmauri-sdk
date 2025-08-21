import pytest
from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


@pytest.mark.acceptance
@pytest.mark.test
def test_plugin_discovery():
    entry = PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY.get(
        "swarmauri.mre_cryptos.PGPSealMreCrypto"
    )
    assert entry == "swarmauri_mre_crypto_pgpseal.PGPSealMreCrypto"
