"""AWS Workforce identity provider implementations."""

from .AwsIdentityResolver import AwsIdentityResolver
from .AwsOAuth20Login import AwsOAuth20Login
from .AwsOAuth21Login import AwsOAuth21Login

__all__ = [
    "AwsOAuth20Login",
    "AwsOAuth21Login",
    "AwsIdentityResolver",
]
