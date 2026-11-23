import requests


def build_prepared_request(method, url, **kwargs):
    return requests.Request(method=method, url=url, **kwargs).prepare()


def build_session(**kwargs):
    session = requests.Session()
    for key, value in kwargs.items():
        if key == "cookies":
            session.cookies.update(value)
        else:
            setattr(session, key, value)
    return session
