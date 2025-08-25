import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from auto_authn.v2.crypto import hash_pw
from auto_authn.v2.orm.tables import ApiKey, Tenant, User


@pytest.mark.integration
class TestRFC7662Introspection:
    """Verify API key introspection endpoint complies with RFC 7662."""

    @pytest.mark.asyncio
    @pytest.mark.xfail(reason="RFC 7662 compliance planned")
    async def test_introspect_valid_api_key_returns_active_true(
        self, async_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Valid API key introspection should report an active token."""
        tenant = Tenant(
            slug="rfc-tenant", name="RFC Tenant", email="tenant_rfc@example.com"
        )
        db_session.add(tenant)
        await db_session.commit()

        user = User(
            tenant_id=tenant.id,
            username="rfcuser",
            email="rfcuser@example.com",
            password_hash=hash_pw("TestPassword123!"),
        )
        db_session.add(user)
        await db_session.commit()

        raw_key = "rfc-7662-api-key"
        api_key = ApiKey(user_id=user.id, label="RFC Key")
        api_key.raw_key = raw_key
        db_session.add(api_key)
        await db_session.commit()

        response = await async_client.post(
            "/apikeys/introspect", json={"api_key": raw_key}
        )

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["active"] is True

    @pytest.mark.asyncio
    @pytest.mark.xfail(reason="RFC 7662 compliance planned")
    async def test_introspect_invalid_api_key_returns_inactive(
        self, async_client: AsyncClient
    ) -> None:
        """Invalid API key introspection should report inactive token."""
        response = await async_client.post(
            "/apikeys/introspect", json={"api_key": "does-not-exist"}
        )

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["active"] is False
