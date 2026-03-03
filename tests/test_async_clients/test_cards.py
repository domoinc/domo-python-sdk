"""Tests for AsyncCardClient using respx to mock httpx requests."""
from __future__ import annotations

import pytest
import respx
from httpx import Response

from domo_sdk.async_clients.cards import AsyncCardClient
from domo_sdk.models.cards import Card
from domo_sdk.transport.async_transport import AsyncTransport
from domo_sdk.transport.auth import (
    DeveloperTokenCredentials,
    DeveloperTokenStrategy,
)


def _make_async_client() -> tuple[AsyncCardClient, str]:
    creds = DeveloperTokenCredentials(
        token="test-token", instance_domain="test.domo.com"
    )
    strategy = DeveloperTokenStrategy(credentials=creds)
    transport = AsyncTransport(auth=strategy)
    client = AsyncCardClient(transport)
    base_url = strategy.get_base_url()
    return client, base_url


@pytest.mark.asyncio
class TestAsyncCardCRUD:
    @respx.mock
    async def test_create(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(f"{base_url}/v1/cards").mock(
            return_value=Response(
                200, json={"id": 1, "title": "Sales Card"}
            )
        )

        result = await client.create({"title": "Sales Card"})

        assert route.called
        assert isinstance(result, Card)
        assert result.name == "Sales Card"
        await client.transport.close()

    @respx.mock
    async def test_get(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(f"{base_url}/v1/cards/1").mock(
            return_value=Response(
                200, json={"id": 1, "title": "Sales Card"}
            )
        )

        result = await client.get(1)

        assert route.called
        assert isinstance(result, Card)
        assert result.id == 1
        await client.transport.close()

    @respx.mock
    async def test_list(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(f"{base_url}/v1/cards").mock(
            return_value=Response(
                200,
                json=[{"id": 1, "title": "A"}, {"id": 2, "title": "B"}],
            )
        )

        result = await client.list()

        assert route.called
        assert len(result) == 2
        assert all(isinstance(c, Card) for c in result)
        await client.transport.close()

    @respx.mock
    async def test_update(self) -> None:
        client, base_url = _make_async_client()
        route = respx.put(f"{base_url}/v1/cards/1").mock(
            return_value=Response(
                200, json={"id": 1, "title": "Updated"}
            )
        )

        result = await client.update(1, {"title": "Updated"})

        assert route.called
        assert isinstance(result, Card)
        assert result.name == "Updated"
        await client.transport.close()

    @respx.mock
    async def test_delete(self) -> None:
        client, base_url = _make_async_client()
        route = respx.delete(f"{base_url}/v1/cards/1").mock(
            return_value=Response(204)
        )

        await client.delete(1)

        assert route.called
        await client.transport.close()
