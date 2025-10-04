class AppleOAuth20AppClient:
    """
    Not supported: Apple Sign In does not offer a client-credentials style server-to-server grant.
    Use user-login flows (OIDC/OAuth) and refresh tokens, or Apple Business/Enterprise alternatives.
    """
    def __init__(self, *_, **__):
        raise NotImplementedError("Apple does not support generic M2M app clients via client_credentials.")
