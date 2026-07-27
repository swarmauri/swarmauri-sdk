from swarmauri_provider_qwen import QwenProvider


def test_provider_defaults():
    assert QwenProvider().catalog.get_model("qwen-omni-turbo-realtime")
