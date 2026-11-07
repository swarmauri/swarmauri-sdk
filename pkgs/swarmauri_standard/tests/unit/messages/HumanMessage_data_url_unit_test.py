"""Verify that HumanMessage preserves already encoded image data URLs."""

from swarmauri_standard.messages.HumanMessage import HumanMessage


def test_image_data_url_is_preserved_without_filesystem_encoding():
    """Keep base64 image inputs intact for multimodal providers."""
    url = "data:image/png;base64,AA=="
    message = HumanMessage(
        content=[{"type": "image_url", "image_url": {"url": url}}]
    )
    assert message.content[0]["image_url"]["url"] == url
