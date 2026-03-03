"""Tests for AsyncAccountClient using respx to mock httpx requests."""
from __future__ import annotations

import pytest
import respx
from httpx import Response

from domo_sdk.async_clients.accounts import AsyncAccountClient
from domo_sdk.models.accounts import Account
from domo_sdk.transport.async_transport import AsyncTransport
from domo_sdk.transport.auth import (
    DeveloperTokenCredentials,
    DeveloperTokenStrategy,
)


def _make_async_client() -> tuple[AsyncAccountClient, str]:
    creds = DeveloperTokenCredentials(
        token="test-token", instance_domain="test.domo.com"
    )
    strategy = DeveloperTokenStrategy(credentials=creds)
    transport = AsyncTransport(auth=strategy)
    client = AsyncAccountClient(transport)
    base_url = strategy.get_base_url()
    return client, base_url


@pytest.mark.asyncio
class TestAsyncAccountCRUD:
    @respx.mock
    async def test_create(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(f"{base_url}/v1/accounts").mock(
            return_value=Response(
                200, json={"id": "1", "name": "Snowflake"}
            )
        )

        result = await client.create(name="Snowflake")

        assert route.called
        assert isinstance(result, Account)
        assert result.name == "Snowflake"
        await client.transport.close()

    @respx.mock
    async def test_get(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(f"{base_url}/v1/accounts/1").mock(
            return_value=Response(
                200, json={"id": "1", "name": "Snowflake"}
            )
        )

        result = await client.get("1")

        assert route.called
        assert isinstance(result, Account)
        assert result.id == "1"
        await client.transport.close()

    @respx.mock
    async def test_list(self) -> None:
        client, base_url = _make_async_client()
        respx.get(f"{base_url}/v1/accounts").mock(
            side_effect=[
                Response(
                    200,
                    json=[
                        {"id": "1", "name": "A"},
                        {"id": "2", "name": "B"},
                    ],
                ),
                Response(200, json=[]),
            ]
        )

        result = await client.list()

        assert len(result) == 2
        assert all(isinstance(a, Account) for a in result)
        await client.transport.close()

    @respx.mock
    async def test_delete(self) -> None:
        client, base_url = _make_async_client()
        route = respx.delete(f"{base_url}/v1/accounts/1").mock(
            return_value=Response(204)
        )

        await client.delete("1")

        assert route.called
        await client.transport.close()
