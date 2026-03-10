from tigrbl_base._base._headers_base import HeaderCookiesBase, HeadersBase


def test_headers_base_types() -> None:
    headers = HeadersBase({"content-type": "application/json"})
    cookies = HeaderCookiesBase({"sid": "abc"})

    assert isinstance(headers, dict)
    assert headers["content-type"] == "application/json"
    assert isinstance(cookies, dict)
    assert cookies["sid"] == "abc"
