import httpx


def build_prepared_request(method, url, **kwargs):
    return httpx.Request(method=method, url=url, **kwargs)


def build_session(**kwargs):
    return httpx.Client(**kwargs)
