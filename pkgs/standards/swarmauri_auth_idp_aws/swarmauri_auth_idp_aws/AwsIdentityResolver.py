"""Helper for resolving IAM Identity Center identity details using AWS APIs."""

from __future__ import annotations

from typing import Dict

import boto3
import requests


class AwsIdentityResolver:
    """Resolve IAM Identity Center identities via AWS APIs."""

    def __init__(
        self,
        *,
        region: str,
        sso_region: str,
        identity_store_id: str,
        account_id: str,
        role_name: str,
    ) -> None:
        self.region = region
        self.sso_region = sso_region
        self.identity_store_id = identity_store_id
        self.account_id = account_id
        self.role_name = role_name

    def _get_role_credentials(self, access_token: str) -> Dict[str, str]:
        url = (
            f"https://portal.sso.{self.sso_region}.amazonaws.com/federation/credentials"
        )
        response = requests.get(
            url,
            params={"account_id": self.account_id, "role_name": self.role_name},
            headers={"x-amz-sso_bearer_token": access_token},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["roleCredentials"]

    def lookup_user_min(self, access_token: str) -> Dict[str, object]:
        creds = self._get_role_credentials(access_token)
        session = boto3.Session(
            aws_access_key_id=creds["accessKeyId"],
            aws_secret_access_key=creds["secretAccessKey"],
            aws_session_token=creds["sessionToken"],
            region_name=self.region,
        )
        identitystore = session.client("identitystore")
        response = identitystore.list_users(
            IdentityStoreId=self.identity_store_id, MaxResults=1
        )
        user = response["Users"][0]
        emails = [entry.get("Value") for entry in user.get("Emails", [])]
        return {
            "userId": user.get("UserId"),
            "userName": user.get("UserName"),
            "displayName": user.get("DisplayName"),
            "emails": emails,
        }
