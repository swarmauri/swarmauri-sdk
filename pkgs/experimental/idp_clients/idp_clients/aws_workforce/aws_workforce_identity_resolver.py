from __future__ import annotations
from dataclasses import dataclass
import boto3, requests

@dataclass(frozen=True)
class AwsWorkforceIdentityResolver:
    region: str
    sso_region: str
    identity_store_id: str
    account_id: str        # account that hosts the reader role
    role_name: str         # reader role assigned to all users

    def _get_role_credentials(self, access_token: str) -> dict:
        url = f"https://portal.sso.{self.sso_region}.amazonaws.com/federation/credentials"
        r = requests.get(url, params={"account_id": self.account_id, "role_name": self.role_name},
                         headers={"x-amz-sso_bearer_token": access_token}, timeout=30)
        r.raise_for_status()
        return r.json()["roleCredentials"]

    def lookup_user_min(self, access_token: str) -> dict:
        creds = self._get_role_credentials(access_token)
        sess = boto3.Session(
            aws_access_key_id=creds["accessKeyId"],
            aws_secret_access_key=creds["secretAccessKey"],
            aws_session_token=creds["sessionToken"],
            region_name=self.region,
        )
        idc = sess.client("identitystore")
        resp = idc.list_users(IdentityStoreId=self.identity_store_id, MaxResults=1)  # demo only
        user = resp["Users"][0]
        return {
            "userId": user.get("UserId"),
            "userName": user.get("UserName"),
            "displayName": user.get("DisplayName"),
            "emails": [e.get("Value") for e in user.get("Emails", [])],
        }
