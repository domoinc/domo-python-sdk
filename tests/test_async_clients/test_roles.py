"""Tests for AsyncRolesClient using respx to mock httpx requests."""
from __future__ import annotations

import pytest
import respx
from httpx import Response

from domo_sdk.async_clients.roles import AsyncRolesClient
from domo_sdk.models.roles import Authority, Role
from domo_sdk.transport.async_transport import AsyncTransport
from domo_sdk.transport.auth import (
    DeveloperTokenCredentials,
    DeveloperTokenStrategy,
)


def _make_async_client() -> tuple[AsyncRolesClient, str]:
    creds = DeveloperTokenCredentials(
        token="test-token", instance_domain="test.domo.com"
    )
    strategy = DeveloperTokenStrategy(credentials=creds)
    transport = AsyncTransport(auth=strategy)
    client = AsyncRolesClient(transport)
    base_url = strategy.get_base_url()
    return client, base_url


@pytest.mark.asyncio
class TestAsyncRolesCRUD:
    @respx.mock
    async def test_list(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(f"{base_url}/authorization/v1/roles").mock(
            return_value=Response(
                200,
                json=[{"id": 1, "name": "Admin"}, {"id": 2, "name": "User"}],
            )
        )

        result = await client.list()

        assert route.called
        assert len(result) == 2
        assert all(isinstance(r, Role) for r in result)
        await client.transport.close()

    @respx.mock
    async def test_create(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(f"{base_url}/authorization/v1/roles").mock(
            return_value=Response(200, json={"id": 3, "name": "Custom"})
        )

        result = await client.create({"name": "Custom"})

        assert route.called
        assert isinstance(result, Role)
        assert result.name == "Custom"
        await client.transport.close()

    @respx.mock
    async def test_get(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(f"{base_url}/authorization/v1/roles/1").mock(
            return_value=Response(200, json={"id": 1, "name": "Admin"})
        )

        result = await client.get(1)

        assert route.called
        assert isinstance(result, Role)
        assert result.id == 1
        await client.transport.close()

    @respx.mock
    async def test_delete(self) -> None:
        client, base_url = _make_async_client()
        route = respx.delete(f"{base_url}/authorization/v1/roles/1").mock(
            return_value=Response(204)
        )

        await client.delete(1)

        assert route.called
        await client.transport.close()


@pytest.mark.asyncio
class TestAsyncRolesAuthorities:
    @respx.mock
    async def test_list_authorities(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(
            f"{base_url}/authorization/v1/roles/1/authorities"
        ).mock(
            return_value=Response(
                200,
                json=[{"id": 1, "authority": "DATA"}],
            )
        )

        result = await client.list_authorities(1)

        assert route.called
        assert len(result) == 1
        assert isinstance(result[0], Authority)
        await client.transport.close()

    @respx.mock
    async def test_update_authorities(self) -> None:
        client, base_url = _make_async_client()
        route = respx.patch(
            f"{base_url}/authorization/v1/roles/1/authorities"
        ).mock(
            return_value=Response(
                200,
                json=[{"id": 1, "authority": "DATA"}],
            )
        )

        result = await client.update_authorities(
            1, [{"authority": "DATA"}]
        )

        assert route.called
        assert len(result) == 1
        assert isinstance(result[0], Authority)
        await client.transport.close()
