from __future__ import annotations
import time, httpx, jwt
from dataclasses import dataclass

@dataclass(frozen=True)
class GitHubAppClient:
    app_id: str                    # GitHub App ID (numeric)
    private_key_pem: bytes         # App private key (PEM)
    api_base: str = "https://api.github.com"

    def _app_jwt(self) -> str:
        now = int(time.time())
        payload = {"iat": now - 60, "exp": now + 600, "iss": self.app_id}
        return jwt.encode(payload, self.private_key_pem, algorithm="RS256")

    async def installation_token(self, installation_id: int) -> str:
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(
                f"{self.api_base}/app/installations/{installation_id}/access_tokens",
                headers={"Authorization": f"Bearer {self._app_jwt()}",
                         "Accept": "application/vnd.github+json"})
            r.raise_for_status()
            return r.json()["token"]
