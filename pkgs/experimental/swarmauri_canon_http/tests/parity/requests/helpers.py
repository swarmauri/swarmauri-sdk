import requests


def build_prepared_request(method, url, **kwargs):
    request = requests.Request(method=method, url=url, **kwargs)
    session = requests.Session()
    prepared = session.prepare_request(request)
    session.close()
    return prepared


def build_session(**kwargs):
    session = requests.Session()
    for key, value in kwargs.items():
        setattr(session, key, value)
    return session
