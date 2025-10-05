class FacebookOIDC10AppClient:
    """
    Not supported / not typical: Facebook's OIDC is for user sign-in.
    There is no general-purpose client_credentials OIDC flow for Facebook.
    Use the OAuth 2.0 App Client below for app-level tokens.
    """
    def __init__(self, *_, **__):
        raise NotImplementedError("Facebook OIDC app client (client_credentials) is not supported.")
