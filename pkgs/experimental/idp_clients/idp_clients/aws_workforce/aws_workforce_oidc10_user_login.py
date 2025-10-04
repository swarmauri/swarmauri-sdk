class AwsWorkforceOIDC10Login:
    """Not supported: IAM Identity Center does not issue OIDC ID tokens/UserInfo."""
    def __init__(self, *_, **__):
        raise NotImplementedError("OIDC 1.0 user login is not supported by AWS IAM Identity Center.")
